from abc import ABC, abstractmethod
from typing import List, Dict

class Agent(ABC):
    def __init__(self, name: str, personality_description: str):
        self.name = name
        self.personality_description = personality_description

    @abstractmethod
    def generate_response(self, conversation_history: List[Dict[str, str]]) -> str:
        """
        Generates a response based on the conversation history.
        conversation_history: List of dicts with 'role' and 'content'.
        """
        pass
