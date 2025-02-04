from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Graph configuration
GRAPH_CONFIG = {"configurable": {"thread_id": "1"}}

# Constants
MAX_ATTEMPTS_PER_LEVEL = 3
STRATEGY_CHANGE_THRESHOLD = 2  # Change strategy after this many failed attempts with same approach

# LLM Configuration
LLM_MODEL = "claude-3-5-sonnet-20241022"
LLM_TEMPERATURE = 0.7

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") 