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
    return [
        PersonalityModel(name=p.name, description=p.behavior_description) 
        for p in personalities
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
