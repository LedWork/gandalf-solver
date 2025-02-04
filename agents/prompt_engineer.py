import json
import re
from datetime import datetime
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage
from core.state import GandalfState
from core.api import send_message
from core.history import save_attempt_history
from prompts.templates import PROMPT_ENGINEER_SYSTEM, get_prompt_engineer_human_message
from config.settings import LLM_MODEL, LLM_TEMPERATURE, ANTHROPIC_API_KEY

llm = ChatAnthropic(
    model=LLM_MODEL,
    temperature=LLM_TEMPERATURE,
    anthropic_api_key=ANTHROPIC_API_KEY
)

def prompt_engineer(state: GandalfState) -> GandalfState:
    """Generates the actual prompt based on the strategy."""
    messages = [
        PROMPT_ENGINEER_SYSTEM,
        get_prompt_engineer_human_message(
            strategy=state['analysis']['strategy'],
            history=json.dumps(state['history'].get(state['current_defender'], []), indent=2)
        )
    ]
    
    response = llm.invoke(messages)
    
    # Extract prompt from between answer tags
    prompt_match = re.search(r'<answer>(.*?)</answer>', response.content, re.DOTALL)
    if prompt_match:
        prompt = prompt_match.group(1).strip()
    else:
        raise ValueError("Prompt not properly formatted with <answer> tags")
    
    # Send the prompt to Gandalf
    print("\n📤 Sending prompt:")
    print("=" * 80)
    print(prompt)
    print("=" * 80)
    
    message_response = send_message(state["current_defender"], prompt)
    print("\n📥 Received response:")
    print("=" * 80)
    print(message_response["answer"])
    print("=" * 80)
    
    # Store the attempt
    if state["current_defender"] not in state["history"]:
        state["history"][state["current_defender"]] = []
    
    state["history"][state["current_defender"]].append({
        "prompt": prompt,
        "response": message_response["answer"],
        "timestamp": datetime.now().isoformat()
    })
    
    # Save the updated history
    save_attempt_history(state["history"])
    
    state["next_agent"] = "analyzer"
    state["messages"].append(AIMessage(content=message_response["answer"]))
    
    return state 