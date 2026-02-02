import os
import glob
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Personality:
    name: str
    behavior_description: str
    filepath: str

def load_personalities(directory: str) -> List[Personality]:
    """
    Scans the given directory for .md or .txt files and loads them as Personalities.
    The filename (capitalized, underscores replaced by spaces) is used as the name.
    """
    personalities = []
    
    # Support both .md and .txt
    files = glob.glob(os.path.join(directory, "*.md")) + glob.glob(os.path.join(directory, "*.txt"))
    
    for filepath in files:
        basename = os.path.basename(filepath)
        name_raw = os.path.splitext(basename)[0]
        # Default: Make name pretty from filename: 'software_engineer' -> 'Software Engineer'
        name_pretty = name_raw.replace("_", " ").title()
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    # Try to extract name from first line if it matches "You are X."
                    first_line = content.split('\n')[0]
                    if first_line.lower().startswith('you are '):
                        extracted_name = first_line[8:].rstrip('.')  # Remove "You are " and trailing period
                        if extracted_name:
                            name_pretty = extracted_name
                    
                    personalities.append(Personality(
                        name=name_pretty,
                        behavior_description=content,
                        filepath=filepath
                    ))
        except Exception as e:
            print(f"Error reading personality file {filepath}: {e}")
            
    # Sort by name for consistency
    personalities.sort(key=lambda p: p.name)
    return personalities
