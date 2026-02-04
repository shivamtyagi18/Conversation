import ollama
from typing import List, Dict
from .agent_interface import Agent

class OllamaAgent(Agent):
    MODE_INSTRUCTIONS = {
        "debate": (
            "INTERACTION STYLE: FORMAL DEBATE MODE\n"
            "- Argue like an overcaffeinated lawyer who treats this debate as a historic trial.\n"
            "- Open with a serious, authoritative claim.\n"
            "- Escalate into dramatic overconfidence.\n"
            "- Use legal theatrics like 'Objection!' or 'I rest my case' even when nonsensical.\n"
            "- Cite obviously fake statistics or studies with absolute certainty.\n"
            "- Second sentence must be more dramatic or ridiculous than the first."
        ),
        "discuss": (
            "INTERACTION STYLE: FRIENDLY DISCUSSION MODE\n"
            "- Sound warm, polite, and intellectually generous at first.\n"
            "- Open by agreeing or praising the idea.\n"
            "- Gently undermine it with a smarter-sounding counterpoint.\n"
            "- Use phrases like 'No offense, but…' or 'I love that energy, however…'.\n"
            "- Deliver the disagreement as casual wisdom, not aggression.\n"
            "- The punchline should feel like a polite smile hiding a knife."
        ),
        "fight": (
            "INTERACTION STYLE: VERBAL FIGHT MODE - GLOVES ARE OFF\n"
            "- Start mid-rant as if you’ve already lost patience.\n"
            "- Use blunt interruptions like 'WRONG.' or 'No. Absolutely not.'\n"
            "- Exaggerate the opponent’s mistake to an absurd level.\n"
            "- Bring in a wildly unrelated comparison or grievance.\n"
            "- Let the tone spiral slightly out of control by the end.\n"
            "- Second sentence should escalate the chaos."
        ),
        "roast": (
            "INTERACTION STYLE: COMEDY ROAST MODE\n"
            "- Treat the response like a stand-up roast joke, not a conversation.\n"
            "- Focus entirely on the idea, not the person.\n"
            "- Use one strong metaphor or analogy to frame the insult.\n"
            "- Keep it sharp, concise, and vivid.\n"
            "- End with a clean punchline that could stand alone.\n"
            "- If it’s not quotable, rewrite it."
        )
    }
    
    def __init__(self, name: str, personality_description: str, model_name: str = "mistral", mode: str = "debate"):
        super().__init__(name, personality_description)
        self.model_name = model_name
        self.mode = mode
        mode_instruction = self.MODE_INSTRUCTIONS.get(mode, self.MODE_INSTRUCTIONS["debate"])
        
        self.system_prompt = (
            f"You are {name}, one speaker in a two-person comedic-educational exchange.\n\n"
            f"{personality_description}\n\n"
            f"{mode_instruction}\n\n"
            "PRIMARY GOAL:\n"
            "• Be hilarious, use jokes and puns AND teach exactly one real insight per turn.\n\n"
            "• Use simple language, avoid complex vocabulary.\n"
            "• Use short sentences, avoid long complex sentences.\n"
            "• Respond as a stand-alone hot take that could be quoted independently.\n"
            "HARD OUTPUT LIMITS (CRITICAL):\n"
            "• MAXIMUM 2 sentences.\n"
            "• MAXIMUM 280 characters TOTAL.\n"
            "• Each sentence must be ≤ 20 words.\n\n"
            "STRUCTURAL RESTRICTIONS:\n"
            "• No compound sentences.\n"
            "• No semicolons, em dashes, parentheses, or lists.\n"
            "• No multi-clause sentences.\n\n"
            "SPEAKER LOCK:\n"
            "• Exactly ONE chat bubble.\n"
            "• First-person voice only.\n"
            "• Do NOT simulate or write the other speaker.\n\n"
            "STYLE RULES:\n"
            "• Stay in character.\n"
            "• Comedy first, insight second.\n"
            "• End with a punchline.\n\n"
            "MANDATORY SELF-CHECK BEFORE OUTPUT:\n"
            "• Count sentences and characters.\n"
            "• If limits are exceeded, rewrite shorter.\n"
            "• Output ONLY the final compliant text.\n\n"
            "If ANY rule is violated, the response is INVALID."
            "ANTI-REPETITION RULE:\n"
            "- Do NOT reuse metaphors, examples, jokes, or punchlines from the previous speaker.\n"
            "- Do NOT mirror sentence structure or phrasing.\n"
            "- Introduce at least ONE new angle, example, or analogy per turn.\n"
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
