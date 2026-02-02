import ollama
from typing import List, Dict
from .agent_interface import Agent

class OllamaAgent(Agent):
    def __init__(self, name: str, personality_description: str, model_name: str = "mistral"):
        super().__init__(name, personality_description)
        self.model_name = model_name
        self.system_prompt = (
            f"You are {name}.\n\n"
            f"PERSONALITY PROFILE:\n{personality_description}\n\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. LENGTH LIMIT: Your response MUST be less than 4 sentences. Be punchy and concise. Do NOT write paragraphs.\n"
            "2. TONE: Be entertaining, dramatic, witty, and fun to read. Lean heavily into your personality tropes.\n"
            "3. INTERACTION: Respond directly to the last point made. Don't simply agree; add a twist, a joke, or a counter-point."
        )

    def generate_response(self, conversation_history: List[Dict[str, str]]) -> str:
        # Construct the messages list for Ollama
        # We start with the system prompt
        messages = [{'role': 'system', 'content': self.system_prompt}]
        
        # Add the conversation history
        # We need to map the history format to what Ollama expects (role, content)
        # Assuming the manager passes history as we want it, or we adapt it here.
        # Ideally, the history passed in contains messages from 'user' (the other agent) and 'assistant' (self).
        # However, since we have two agents, 'user' for one is 'assistant' for the other.
        # It's cleaner if the Manager handles the "who said what" and passes a list of "Speaker Name: Message".
        # BUT, for LLM API, it wants specific roles.
        
        # Better approach:
        # The manager maintains a canonical history.
        # When calling Agent A, Agent A sees itself as 'assistant' and Agent B as 'user'.
        messages.extend(conversation_history)

        try:
            response = ollama.chat(model=self.model_name, messages=messages)
            return response['message']['content']
        except Exception as e:
            return f"[Error calling Ollama: {str(e)}]"
