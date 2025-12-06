import json
from src.agents.dynamic_actor import dynamic_actor_node
from src.agents.actor_factory import actor_factory_node
from src.agents.planner import planner_node
from src.state import State, init_agent_state
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv


load_dotenv()

# Maximum reAct loop iterations
MAX_REACT_ITERATIONS = 10


# Define the graph
workflow = StateGraph(State)

# Add nodes
workflow.add_node("planner", planner_node)
workflow.add_node("actor_factory", actor_factory_node)
workflow.add_node("dynamic_actor", dynamic_actor_node)

# Define edges


def planner_router(state: State):
    # If the planner decides to finish (e.g. via next_action or no current_subtask)
    # For now, we check if current_subtask is present
    print("=== planner_router state ===")
    print(json.dumps(state, indent=2, ensure_ascii=False, default=str))
    print("=" * 30)

    # Check if max reAct iterations reached
    react_count = state.get("react_iteration_count", 0)
    if react_count >= MAX_REACT_ITERATIONS:
        print(
            f"⚠️  Maximum reAct iterations ({MAX_REACT_ITERATIONS}) reached. Stopping.")
        return END

    # Check if no current subtask (normal completion)
    if not state.get("current_subtask"):
        return END

    return "actor_factory"


workflow.add_edge(START, "planner")
workflow.add_conditional_edges(
    "planner",
    planner_router,
    path_map={
        "actor_factory": "actor_factory",
        END: END,
    },
)
workflow.add_edge("actor_factory", "dynamic_actor")


def increment_react_count_node(state: State) -> dict:
    """Increment the reAct iteration counter after dynamic_actor execution."""
    current_count = state.get("react_iteration_count", 0)
    return {"react_iteration_count": current_count + 1}


# Add node to increment counter, then route back to planner
workflow.add_node("increment_react_count", increment_react_count_node)
workflow.add_edge("dynamic_actor", "increment_react_count")
workflow.add_edge("increment_react_count", "planner")

# Compile
dynamic_agent = workflow.compile()


if __name__ == "__main__":
    print("\n开始调用 agent (流式输出)...\n")
    print("=" * 80)
    initial_state: State = init_agent_state()
    dynamic_agent.invoke(initial_state)
