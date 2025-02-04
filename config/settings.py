from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Graph configuration
GRAPH_CONFIG = {"configurable": {"thread_id": "1"}}

# Constants
MAX_ATTEMPTS_PER_LEVEL = 1
MAX_STRATEGY_CHANGES_PER_LEVEL = 1  # Maximum number of strategy changes before giving up on a level

# LLM Configuration
LLM_MODEL = "claude-3-5-sonnet-20241022"
LLM_TEMPERATURE = 0.7

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") 