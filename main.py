import os
import sys

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.personality_loader import load_personalities
from core.ollama_client import OllamaAgent
from core.manager import ConversationManager
from utils.display import console, print_welcome, print_personalities, select_personality, get_topic, print_turn

def main():
    print_welcome()
    
    # Load Personalities
    personalities_dir = os.path.join(os.path.dirname(__file__), 'data', 'personalities')
    personalities = load_personalities(personalities_dir)
    
    if not personalities:
        console.print("[red]No personalities found! Check data/personalities directory.[/red]")
        return
    
    print_personalities(personalities)
    
    # Select Agents
    p1 = select_personality(personalities, "Select Personality for Agent A")
    console.print(f"Agent A selected: [bold]{p1.name}[/bold]")
    
    p2 = select_personality(personalities, "Select Personality for Agent B")
    console.print(f"Agent B selected: [bold]{p2.name}[/bold]")
    
    # Get Topic
    topic = get_topic()
    
    # Initialize Agents
    # Assuming 'mistral' is pulled. We could make this configurable later.
    agent_a = OllamaAgent(name=p1.name, personality_description=p1.behavior_description)
    agent_b = OllamaAgent(name=p2.name, personality_description=p2.behavior_description)
    
    manager = ConversationManager(agent_a, agent_b, topic)
    
    # Start Loop
    try:
        for agent, message in manager.start_conversation(rounds=5):
            color = "green" if agent == agent_a else "magenta"
            print_turn(agent.name, color, message)
    except KeyboardInterrupt:
        console.print("\n[red]Conversation interrupted by user.[/red]")
    except Exception as e:
        console.print(f"\n[red]An error occurred: {e}[/red]")

if __name__ == "__main__":
    main()
