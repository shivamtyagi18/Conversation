from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown

console = Console()

def print_welcome():
    console.print(Panel.fit("[bold blue]Dual-Agent Discussion Arena[/bold blue]", border_style="blue"))

def print_personalities(personalities):
    console.print("\n[bold]Available Personalities:[/bold]")
    for i, p in enumerate(personalities, 1):
        console.print(f"[green]{i}. {p.name}[/green]: {p.behavior_description.split('.')[0]}.")

def select_personality(personalities, prompt_text: str):
    while True:
        choice = Prompt.ask(f"[bold yellow]{prompt_text} (1-{len(personalities)})[/bold yellow]")
        try:
            index = int(choice) - 1
            if 0 <= index < len(personalities):
                return personalities[index]
            else:
                console.print("[red]Invalid selection. Please try again.[/red]")
        except ValueError:
            console.print("[red]Please enter a number.[/red]")

def get_topic():
    return Prompt.ask("\n[bold cyan]Enter the Topic of Discussion[/bold cyan]")

def print_turn(agent_name: str, color: str, content: str):
    # console.print(f"\n[bold {color}]{agent_name}:[/bold {color}]")
    console.print(Panel(Markdown(content), title=f"[bold {color}]{agent_name}[/bold {color}]", border_style=color))
