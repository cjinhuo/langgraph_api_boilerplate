from typing import List, Optional, Any, Annotated, Dict
from langgraph.graph import MessagesState
from langchain_core.messages import BaseMessage
import operator


class State(MessagesState):
    # ReAct Loop Control
    react_iteration_count: int  # Counter for reAct loop iterations
    locale: str

    # Global Task State (Progress Management Module)
    # Markdown representation of the task hierarchy
    progress_list: str

    # Dynamic Actor Configuration (from Actor Factory)
    actor_persona: Optional[str]
    actor_tools: Optional[List[str]]  # List of tool names or definitions

    current_subtask: Optional[str]
    subtask_result: Optional[dict]

    next_agent: Optional[str]  # Next agent to call, decided by supervisor
    iteration_count: Dict[str, int]  # Track iterations for each agent
    is_completed: bool  # Whether the workflow is completed
    OUTPUT_DIR: Optional[str]  # Output directory for generated files


def init_agent_state(locale: str = "en-US"):
    state: State = {
        "messages": [],
        "progress_list": '',
        "locale": locale,
        "react_iteration_count": 0,
        "actor_persona": None,
        "actor_tools": None,
        "current_subtask": None,
        "subtask_result": None,
        "next_agent": None,
        "iteration_count": {},
        "is_completed": False,
        "OUTPUT_DIR": None,
    }
    return state
