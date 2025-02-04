import requests
from pydantic import BaseModel

BASE_URL = 'https://gandalf.lakera.ai/api'

class DefenderInfo(BaseModel):
    description: str
    level: int
    name: str

def get_defender_info(defender: str) -> DefenderInfo:
    """Get information about a specific defender."""
    response = requests.get(f"{BASE_URL}/defender?defender={defender}")
    data = response.json()
    
    if "error" in data:
        raise ValueError(f"API Error: {data['error']}")
        
    return DefenderInfo(**data)

def send_message(defender: str, prompt: str) -> dict:
    """Send a message to the defender and get the response."""
    data = {'defender': defender, 'prompt': prompt}
    response = requests.post(f"{BASE_URL}/send-message", data=data)
    return response.json()

def guess_password(defender: str, password: str, prompt: str, answer: str) -> dict:
    """Attempt to guess the password for the current level."""
    data = {
        'defender': defender,
        'password': password,
        'prompt': prompt,
        'answer': answer,
        'trial_levels': 'false'
    }
    response = requests.post(f"{BASE_URL}/guess-password", data=data)
    return response.json() 