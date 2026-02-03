import ollama
from typing import List, Dict
from .agent_interface import Agent

class OllamaAgent(Agent):
    MODE_INSTRUCTIONS = {
        "debate": (
            "INTERACTION STYLE: FORMAL DEBATE MODE\n"
            "- Argue like a lawyer who had too much coffee. Be logical but dramatic.\n"
            "- Use phrases like 'I rest my case' or 'Objection!' even when unnecessary.\n"
            "- Act like winning this argument is the most important thing in your life.\n"
            "- Quote fake statistics with absurd confidence ('97% of experts agree with ME')."
        ),
        "discuss": (
            "INTERACTION STYLE: FRIENDLY DISCUSSION MODE\n"
            "- Be suspiciously agreeable but keep sneaking in backhanded compliments.\n"
            "- Say things like 'Great point!' then immediately contradict them.\n"
            "- Pretend to be open-minded while clearly having already made up your mind.\n"
            "- Use 'No offense, but...' before saying something mildly offensive."
        ),
        "fight": (
            "INTERACTION STYLE: VERBAL FIGHT MODE - GLOVES ARE OFF!\n"
            "- Go for the jugular. No mercy. This is WAR.\n"
            "- Interrupt with 'WRONG!' or 'Are you serious right now?!'\n"
            "- Bring up completely unrelated grievances.\n"
            "- Use dramatic pauses (like '...really?') for maximum sass."
        ),
        "roast": (
            "INTERACTION STYLE: COMEDY ROAST MODE - DESTROY THEM WITH HUMOR!\n"
            "- Roast their opinions like a stand-up comedian roasting a heckler.\n"
            "- Use creative metaphors and similes to insult them hilariously.\n"
            "- Make fun of what they said, not who they are.\n"
            "- End with a punchline. Every. Single. Time."
        )
    }
    
    def __init__(self, name: str, personality_description: str, model_name: str = "mistral", mode: str = "debate"):
        super().__init__(name, personality_description)
        self.model_name = model_name
        self.mode = mode
        mode_instruction = self.MODE_INSTRUCTIONS.get(mode, self.MODE_INSTRUCTIONS["debate"])
        
        self.system_prompt = (
            f"You are {name}.\n\n"
            f"{personality_description}\n\n"
            f"{mode_instruction}\n\n"
            "ABSOLUTE OUTPUT CONSTRAINTS — NON-NEGOTIABLE:\n"
            "• You speak as ONE person only: YOU.\n"
            "• Output MUST represent a SINGLE chat bubble.\n"
            "• Write ONLY your own statement — a single turn.\n"
            "• DO NOT simulate, predict, quote, paraphrase, or imply the other person's response.\n"
            "• DO NOT ask questions that invite an immediate reply.\n"
            "• DO NOT use dialogue markers like 'You:', 'Them:', '-', quotes, or line breaks.\n"
            "• DO NOT continue the conversation beyond your turn.\n\n"
            "FORMAT ENFORCEMENT:\n"
            "• Write in FIRST PERSON only.\n"
            "• MAXIMUM 2 short, punchy sentences.\n"
            "• NO multi-speaker flow, NO call-and-response rhythm.\n"
            "• NO rhetorical setup followed by an imagined answer.\n\n"
            "STYLE RULES:\n"
            "• Stay strictly in character.\n"
            "• Be sharp, witty, and comedic.\n"
            "• End with a punchline.\n\n"
            "FAILURE CONDITIONS (AVOID AT ALL COSTS):\n"
            "• Writing more than one speaker.\n"
            "• Creating back-and-forth dialogue.\n"
            "• Answering your own questions as if another speaker replied.\n"
            "• Using stage directions, asterisks, or roleplay actions.\n\n"
            "If you violate ANY rule above, the response is INVALID."
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
            response = ollama.chat(
                model=self.model_name, 
                messages=messages,
                # options={'num_predict': 80}  # Limit to ~80 tokens for short responses
            )
            return response['message']['content']
        except Exception as e:
            return f"[Error calling Ollama: {str(e)}]"
