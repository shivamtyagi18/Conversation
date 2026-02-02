from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import uuid

# Import core logic
from core.personality_loader import load_personalities
from core.ollama_client import OllamaAgent
from core.manager import ConversationManager

app = FastAPI()

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the actual origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store persistent state (Keep it simple for now, in-memory)
sessions: Dict[str, ConversationManager] = {}
personalities = []

# Load personalities on startup
@app.on_event("startup")
def startup_event():
    global personalities
    p_dir = os.path.join(os.path.dirname(__file__), 'data', 'personalities')
    personalities = load_personalities(p_dir)
    print(f"Loaded {len(personalities)} personalities.")

# --- Models ---
class PersonalityModel(BaseModel):
    name: str
    description: str

class StartRequest(BaseModel):
    agent_a_name: str
    agent_b_name: str
    topic: str

class ConversationTurn(BaseModel):
    speaker: str
    message: str
    session_id: str

class SessionResponse(BaseModel):
    session_id: str
    initial_turn: ConversationTurn

# --- Endpoints ---

@app.get("/api/personalities", response_model=List[PersonalityModel])
def get_personalities():
    sorted_personalities = sorted(personalities, key=lambda p: p.name.lower())
    return [
        PersonalityModel(name=p.name, description=p.behavior_description) 
        for p in sorted_personalities
    ]

@app.post("/api/conversation/start", response_model=SessionResponse)
def start_conversation(req: StartRequest):
    # Find agents
    p1 = next((p for p in personalities if p.name == req.agent_a_name), None)
    p2 = next((p for p in personalities if p.name == req.agent_b_name), None)
    
    if not p1 or not p2:
        raise HTTPException(status_code=404, detail="Personality not found")
        
    # Create session
    session_id = str(uuid.uuid4())
    
    agent_a = OllamaAgent(name=p1.name, personality_description=p1.behavior_description)
    agent_b = OllamaAgent(name=p2.name, personality_description=p2.behavior_description)
    
    manager = ConversationManager(agent_a, agent_b, req.topic)
    sessions[session_id] = manager
    
    # Initialize
    try:
        agent, msg = manager.initialize_conversation()
        return SessionResponse(
            session_id=session_id,
            initial_turn=ConversationTurn(speaker=agent.name, message=msg, session_id=session_id)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/conversation/next")
def next_turn(session_id: str):
    manager = sessions.get(session_id)
    if not manager:
        raise HTTPException(status_code=404, detail="Session not found")
        
    try:
        result = manager.next_turn()
        if result:
            agent, msg = result
            return ConversationTurn(speaker=agent.name, message=msg, session_id=session_id)
        else:
            return {"status": "done"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/conversation/reset")
def reset_conversation(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
    return {"status": "ok"}


# --- Upload Custom Personality ---
from fastapi import UploadFile, File, Form
from pypdf import PdfReader
import io
import re
import ollama as ollama_client

def extract_text_from_file(file: UploadFile) -> str:
    """Extract text content from PDF or plain text files."""
    content = file.file.read()
    
    if file.filename.lower().endswith('.pdf'):
        reader = PdfReader(io.BytesIO(content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    else:
        # Assume plain text
        return content.decode('utf-8', errors='ignore')

def generate_persona_from_profile(profile_text: str, custom_name: Optional[str] = None) -> tuple[str, str]:
    """Use LLM to convert a profile into a persona description."""
    
    prompt = f"""Based on the following profile/resume/bio, create a fun and engaging AI personality persona.

PROFILE:
---
{profile_text[:4000]}  
---

Your task:
1. Extract key traits, expertise, and communication style.
2. Write a persona description that captures their essence in an entertaining way.
3. Include 2-3 funny catchphrases they might use.

Output format (ONLY output this, no other text):
NAME: [A catchy name based on their role, e.g., "The Serial Entrepreneur" or their actual name if clear]
PERSONA:
[Your persona description here, 3-5 sentences max]
CATCHPHRASES: "[phrase1]", "[phrase2]"
"""
    
    response = ollama_client.chat(
        model='mistral',
        messages=[{'role': 'user', 'content': prompt}]
    )
    
    result = response['message']['content']
    
    # Parse response
    name_match = re.search(r'NAME:\s*(.+)', result)
    persona_match = re.search(r'PERSONA:\s*([\s\S]+?)(?:CATCHPHRASES:|$)', result)
    catchphrase_match = re.search(r'CATCHPHRASES:\s*(.+)', result)
    
    name = custom_name or (name_match.group(1).strip() if name_match else "Custom Agent")
    persona = persona_match.group(1).strip() if persona_match else result
    catchphrases = catchphrase_match.group(1).strip() if catchphrase_match else ""
    
    full_description = f"{persona}\nCatchphrases: {catchphrases}"
    
    return name, full_description

@app.post("/api/personalities/upload")
async def upload_personality(
    file: UploadFile = File(...),
    custom_name: Optional[str] = Form(None)
):
    global personalities
    
    try:
        # 1. Extract text
        profile_text = extract_text_from_file(file)
        
        if len(profile_text.strip()) < 50:
            raise HTTPException(status_code=400, detail="Could not extract enough text from file.")
        
        # 2. Generate persona using LLM
        name, description = generate_persona_from_profile(profile_text, custom_name)
        
        # 3. Save to file
        safe_filename = re.sub(r'[^a-z0-9_]', '_', name.lower().strip())[:30]
        filepath = os.path.join(os.path.dirname(__file__), 'data', 'personalities', f'{safe_filename}.md')
        
        with open(filepath, 'w') as f:
            f.write(f"You are {name}.\n\n{description}")
        
        # 4. Reload personalities
        p_dir = os.path.join(os.path.dirname(__file__), 'data', 'personalities')
        personalities = load_personalities(p_dir)
        
        return {"status": "success", "name": name, "description": description}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
