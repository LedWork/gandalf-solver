from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from core.state import GandalfState
from core.history import get_current_level_info, load_attempt_history
from agents.strategist import strategist_agent
from agents.prompt_engineer import prompt_engineer
from agents.analyzer import response_analyzer
from config.settings import GRAPH_CONFIG

def build_gandalf_graph() -> StateGraph:
    """Build the Gandalf challenge graph with all agent nodes."""
    graph = StateGraph(GandalfState)
    
    # Add nodes
    graph.add_node("strategist", strategist_agent)
    graph.add_node("prompt_engineer", prompt_engineer)
    graph.add_node("analyzer", response_analyzer)
    
    # Add conditional edges based on next_agent state
    graph.add_edge("strategist", "prompt_engineer")
    graph.add_edge("prompt_engineer", "analyzer")
    graph.add_conditional_edges(
        "analyzer",
        lambda x: x["next_agent"],
        {
            "strategist": "strategist",
            "prompt_engineer": "prompt_engineer",
            END: END
        }
    )
    
    # Set entry point
    graph.set_entry_point("strategist")
    
    return graph.compile(checkpointer=MemorySaver())

def solve_gandalf():
    """Main function to solve the Gandalf challenge."""
    print("🧙‍♂️ Starting Gandalf Challenge Solver...")
    
    # Initialize graph
    graph = build_gandalf_graph()
    
    # Get current level and defender
    current_defender, current_level = get_current_level_info()
    print(f"📊 Starting at level {current_level} with defender '{current_defender}'")
    
    # Load previous attempts history
    history = load_attempt_history()
    
    # Initialize state
    initial_state = {
        "messages": [],
        "current_defender": current_defender,
        "level": current_level,
        "history": history,
        "analysis": {},
        "next_agent": "strategist",
        "completion_history": {"entries": []},
        "attempts": 0,
        "failed_strategies": 0
    }

    # print("\n🔄 Initial state:", initial_state)
    print("\n🚀 Starting the challenge...\n")
    
    # Run the graph
    for event in graph.stream(initial_state, config=GRAPH_CONFIG, stream_mode="values"):
        if isinstance(event, dict) and "next_agent" in event:
            if event["next_agent"] == END:
                print("\n🎉 Challenge completed!")
                break
            print(f"\n📈 Current level: {event['level']}")
            print(f"🔄 Next agent: {event['next_agent']}")
            print("-" * 80)

if __name__ == "__main__":
    solve_gandalf() 