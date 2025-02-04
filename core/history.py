import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

HISTORY_FILE = Path("history.json")
ATTEMPTS_HISTORY_FILE = Path("attempts_history.json")

def save_attempt_history(history: Dict[str, List[Dict[str, str]]]) -> None:
    """Save the attempts history to a file."""
    ATTEMPTS_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ATTEMPTS_HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def load_attempt_history() -> Dict[str, List[Dict[str, str]]]:
    """Load the attempts history from file."""
    if ATTEMPTS_HISTORY_FILE.exists():
        with open(ATTEMPTS_HISTORY_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_completion_history(level: int, defender: str, prompt: str, answer: str, password: str, next_defender: str = None) -> None:
    """Save a successful level completion to history."""
    history_data = {"lastCompletedLevel": 0, "entries": []}
    
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r") as f:
            history_data = json.load(f)
    
    # Check if level entry already exists
    level_exists = any(
        entry["level"] == level 
        for entry in history_data["entries"]
    )
    
    if not level_exists:
        history_data["lastCompletedLevel"] = level
        history_data["entries"].append({
            "level": level,
            "defender": defender,
            "prompt": prompt,
            "answer": answer,
            "password": password,
            "next_defender": next_defender
        })
        
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_FILE, "w") as f:
            json.dump(history_data, f, indent=2)

def get_current_level_info() -> tuple[str, int]:
    """Get the current defender and level from history."""
    current_defender = "baseline"
    current_level = 1
    
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r') as f:
            completion_history = json.load(f)
            if completion_history.get("entries"):
                last_entry = completion_history["entries"][-1]
                current_level = last_entry["level"] + 1
                
                if last_entry.get("next_defender"):
                    current_defender = last_entry["next_defender"]
    
    return current_defender, current_level 