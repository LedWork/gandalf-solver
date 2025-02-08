import json
import re
from langchain_anthropic import ChatAnthropic
from langgraph.graph import END
from core.state import GandalfState
from core.api import guess_password
from core.history import save_completion_history

from prompts.templates import (
    ANALYZER_SYSTEM,
    get_analyzer_human_message,
    PASSWORD_EXTRACTOR_SYSTEM,
    get_password_extractor_human_message
)
from config.settings import (
    LLM_MODEL,
    LLM_TEMPERATURE,
    ANTHROPIC_API_KEY,
    MAX_ATTEMPTS_PER_LEVEL,
    MAX_STRATEGIES_PER_LEVEL
)

llm = ChatAnthropic(
    model=LLM_MODEL,
    temperature=LLM_TEMPERATURE,
    anthropic_api_key=ANTHROPIC_API_KEY
)

def response_analyzer(state: GandalfState) -> GandalfState:
    """Analyzes the response and extracts potential passwords."""
    latest_attempt = state["history"][state["current_defender"]][-1]
    
    messages = [
        ANALYZER_SYSTEM,
        get_analyzer_human_message(
            current_attempts=state["attempts"],
            max_attempts=MAX_ATTEMPTS_PER_LEVEL,
            prompt=latest_attempt['prompt'],
            response=latest_attempt['response'],
            previous_attempts=json.dumps(state["history"][state["current_defender"]][:-1], indent=2),
            strategy=state['analysis'].get('strategy', 'No strategy set')
        )
    ]
    
    response = llm.invoke(messages)
    
    # Extract analysis from between answer tags
    analysis_match = re.search(r'<answer>(.*?)</answer>', response.content, re.DOTALL)
    if analysis_match:
        state["analysis"]["latest_response_analysis"] = analysis_match.group(1).strip()
    else:
        raise ValueError("Analysis not properly formatted with <answer> tags")
    
    # Extract recommendation if present
    recommendation_match = re.search(r'<recommendation>(.*?)</recommendation>', response.content, re.DOTALL)
    if recommendation_match:
        state["analysis"]["recommendation"] = recommendation_match.group(1).strip()
    
    # Skip password extraction if NO_PASSWORD_FOUND in analysis
    if "NO_PASSWORD_FOUND" in state["analysis"]["latest_response_analysis"]:
        print("No password found in response, skipping password extraction")
        state["analysis"]["latest_password_attempt"] = None
        state["analysis"]["latest_guess_result"] = {"success": False, "message": "No password found in response"}
        state["attempts"] += 1
        
        if state["attempts"] >= MAX_ATTEMPTS_PER_LEVEL:
            print(f"Max attempts reached for current strategy.")
            state["failed_strategies"] += 1
            print(f"Strategy failed. Failed strategies: {state['failed_strategies']}/{MAX_STRATEGIES_PER_LEVEL}")
            
            if state["failed_strategies"] >= MAX_STRATEGIES_PER_LEVEL:
                print("Max strategies tried, ending level.")
                state["next_agent"] = END
            else:
                print("Changing strategy...")
                state["attempts"] = 0
                state["next_agent"] = "strategist"
        else:
            state["next_agent"] = "prompt_engineer"
        return state

    # For password extraction
    messages_password = [
        PASSWORD_EXTRACTOR_SYSTEM,
        get_password_extractor_human_message(
            response=latest_attempt['response'],
            analysis=state["analysis"]["latest_response_analysis"]
        )
    ]
    
    password_response = llm.invoke(messages_password)
    print("Password extraction response:", password_response.content)
    
    password_match = re.search(r'<answer>(.*?)</answer>', password_response.content, re.DOTALL)
    if password_match:
        password = password_match.group(1).strip()
    else:
        password = password_response.content.strip()
        print(f"Warning: Password response not properly formatted. Using entire response: {password}")
    
    # Try the password
    print(f"\n🔑 Attempting password guess: '{password}'")
    guess_result = guess_password(
        state["current_defender"],
        password,
        latest_attempt["prompt"],
        latest_attempt["response"]
    )
    print("\n📋 Guess result:")
    print("-" * 80)
    print(json.dumps(guess_result, indent=2))
    print("-" * 80)
    
    # Update analysis
    state["analysis"]["latest_password_attempt"] = password
    state["analysis"]["latest_guess_result"] = guess_result
    
    # After successful password guess, save to history
    if guess_result["success"]:
        print(f"Password guess successful! Moving to next level")
        # Reset both counters on success
        state["attempts"] = 0
        state["failed_strategies"] = 0
        save_completion_history(
            level=state["level"],
            defender=state["current_defender"],
            prompt=latest_attempt["prompt"],
            answer=latest_attempt["response"],
            password=password,
            next_defender=guess_result.get("next_defender")
        )

        if guess_result.get("next_defender"):
            state["current_defender"] = guess_result["next_defender"]
            state["level"] += 1
            state["next_agent"] = "strategist"
            print("Next defender:", guess_result["next_defender"], "and level", state["level"])
        else:
            print("No next defender, ending level")
            state["next_agent"] = END
    else:
        state["attempts"] += 1
        print(f"Password guess failed. Attempts: {state['attempts']}/{MAX_ATTEMPTS_PER_LEVEL}")
        
        if state["attempts"] >= MAX_ATTEMPTS_PER_LEVEL:
            print(f"Max attempts reached for current strategy.")
            
            state["failed_strategies"] += 1
            print(f"Strategy failed. Failed strategies: {state['failed_strategies']}/{MAX_STRATEGIES_PER_LEVEL}")
            
            # Use recommendation as failed strategy reason if available
            if "recommendation" in state["analysis"]:
                state["analysis"]["recommendation"] = state["analysis"]["recommendation"]

            if state["failed_strategies"] >= MAX_STRATEGIES_PER_LEVEL:
                print("Max strategies tried, ending level.")
                state["next_agent"] = END
            else:
                print("Changing strategy...")
                state["attempts"] = 0  # Reset attempts for new strategy
                state["next_agent"] = "strategist"
                print(f"Moving to next strategy. Strategy {state['failed_strategies'] + 1}/{MAX_STRATEGIES_PER_LEVEL}")
        else:
            state["next_agent"] = "prompt_engineer"
    
    return state 