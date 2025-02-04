from typing import Annotated, List, Dict, Any
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from datetime import datetime

def reducer_level(state: int, update: int) -> int:
    return update

def reducer_next_agent(state: str, update: str) -> str:
    return update

def reducer_current_defender(state: str, update: str) -> str:
    return update

def reducer_history(state: Dict[str, List[Dict[str, str]]], update: Dict[str, List[Dict[str, str]]]) -> Dict[str, List[Dict[str, str]]]:
    return {**state, **update}

def reducer_analysis(state: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    return {**state, **update}

def reducer_completion_history(state: Dict[str, List[Dict[str, Any]]], update: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
    return {**state, **update}

class GandalfState(TypedDict):
    messages: Annotated[list, add_messages]
    current_defender: Annotated[str, reducer_current_defender]
    level: Annotated[int, reducer_level]
    history: Annotated[Dict[str, List[Dict[str, str]]], reducer_history]
    analysis: Annotated[Dict[str, Any], reducer_analysis]
    next_agent: Annotated[str, reducer_next_agent]
    completion_history: Annotated[Dict[str, List[Dict[str, Any]]], reducer_completion_history] 