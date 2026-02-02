from typing import List, Dict
from .agent_interface import Agent
import time

class ConversationManager:
    def __init__(self, agent_a: Agent, agent_b: Agent, topic: str):
        self.agent_a = agent_a
        self.agent_b = agent_b
        self.topic = topic
        self.history_canonical = [] # List of {"name": str, "message": str}

    def initialize_conversation(self):
        """
        Initializes the conversation and returns the first message from Agent A.
        """
        print(f"\n--- Starting Discussion on: '{self.topic}' ---\n")
        
        # Initial trigger for Agent A
        initial_history_for_a = [
            {'role': 'user', 'content': f"Please discuss the following topic with {self.agent_b.name}: {self.topic}"}
        ]
        
        response_a = self.agent_a.generate_response(initial_history_for_a)
        self._record_message(self.agent_a, response_a)
        
        # Set up state for next turn
        self.next_speaker = self.agent_b
        self.other_agent = self.agent_a
        
        return self.agent_a, response_a

    def next_turn(self):
        """
        Executes a single turn of the conversation.
        Returns (speaker, message) or None if error/done.
        """
        if not hasattr(self, 'next_speaker'):
            return None

        # Build history for current_speaker
        history_for_llm = [{'role': 'user', 'content': f"Topic: {self.topic}"}]
        
        for entry in self.history_canonical:
            role = 'assistant' if entry['name'] == self.next_speaker.name else 'user'
            content = entry['message']
            if role == 'user':
                content = f"{entry['name']}: {content}"
            
            history_for_llm.append({'role': role, 'content': content})
        
        # Generate response
        response = self.next_speaker.generate_response(history_for_llm)
        self._record_message(self.next_speaker, response)
        
        # Return result before swapping
        result = (self.next_speaker, response)
        
        # Swap turns
        self.next_speaker, self.other_agent = self.other_agent, self.next_speaker
        
        return result

    def start_conversation(self, rounds: int = 5):
        # Legacy method for CLI
        agent, msg = self.initialize_conversation()
        yield (agent, msg)
        
        for _ in range(rounds * 2 - 1):
             yield self.next_turn()
    def _record_message(self, agent: Agent, message: str):
        self.history_canonical.append({"name": agent.name, "message": message})
