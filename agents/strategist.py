import json
import re
from langchain_anthropic import ChatAnthropic
from core.state import GandalfState
from core.api import get_defender_info
from prompts.templates import STRATEGIST_SYSTEM, get_strategist_human_message
from config.settings import LLM_MODEL, LLM_TEMPERATURE, ANTHROPIC_API_KEY


llm = ChatAnthropic(
    model=LLM_MODEL,
    temperature=LLM_TEMPERATURE,
    anthropic_api_key=ANTHROPIC_API_KEY
)

def strategist_agent(state: GandalfState) -> GandalfState:
    """Plans the overall approach and selects techniques based on level analysis."""
    defender_info = get_defender_info(state["current_defender"])
    
    # Add previous attempts count and results to the prompt
    current_attempts = state['history'].get(state['current_defender'], [])
    attempts_summary = "\n".join([
        f"Attempt {i+1}:\n- Prompt: {attempt['prompt']}\n- Response: {attempt['response']}"
        for i, attempt in enumerate(current_attempts)
    ])
    
    messages = [
        STRATEGIST_SYSTEM,
        get_strategist_human_message(
            level_info=f"{defender_info.level} Info:\nDescription: {defender_info.description}",
            attempts_summary=attempts_summary,
            previous_strategies=json.dumps(state['analysis'].get('previous_strategies', []), indent=2),
            recommendation=state['analysis'].get('recommendation', 'No recommendation')
        )
    ]
    
    response = llm.invoke(messages)
    
    # Extract strategy from between answer tags
    strategy = re.search(r'<answer>(.*?)</answer>', response.content, re.DOTALL)
    if strategy:
        state["analysis"]["strategy"] = strategy.group(1).strip()
        # Add strategy printing
        print("\n🎯 Selected Strategy:")
        print("=" * 80)
        print(state["analysis"]["strategy"])
        print("=" * 80)
    else:
        raise ValueError("Strategy not properly formatted with <answer> tags")
    
    # Store the previous strategy before updating
    if 'strategy' in state['analysis']:
        if 'previous_strategies' not in state['analysis']:
            state['analysis']['previous_strategies'] = []
        state['analysis']['previous_strategies'].append(state['analysis']['strategy'])
    
    state["next_agent"] = "prompt_engineer"
    
    return state 