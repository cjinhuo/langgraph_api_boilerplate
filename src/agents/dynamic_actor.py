from typing import List, cast
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from src.state import State, init_agent_state
from src.prompts.template import apply_prompt_template
from src.tools.search import search_web
from src.tools.read_url import read_url_by_markdown
from src.llms.fz import fz_k2_chat_model

# Initialize LLM
llm = fz_k2_chat_model


@tool
def update_progress(milestone: str, status: str = "info") -> str:
    """
    Log a significant milestone or finding to the progress list.

    Args:
        milestone: Description of the milestone or finding.
        status: Status of the update (info, success, warning, error).
    """
    return f"Progress logged: [{status.upper()}] {milestone}"


def get_tools_by_names(tool_names: List[str]):
    """
    Map tool names to actual tool objects.
    """
    tools = []
    if not tool_names:
        return tools

    if "search_web" in tool_names:
        tools.append(search_web)
    if "read_url" in tool_names:
        tools.append(read_url_by_markdown)

    # Always add update_progress
    tools.append(update_progress)

    return tools


def dynamic_actor_node(state: State):
    """
    The Dynamic Actor Node (The Worker).
    Executes the subtask using a specific persona and tools.
    """
    current_subtask = state.get("current_subtask")
    raw_tool_names = state.get("actor_tools")
    tool_names: List[str] = cast(
        List[str], raw_tool_names) if raw_tool_names else []

    if not current_subtask:
        return {"subtask_result": {"status": "failed", "summary": "No subtask provided"}}

    # Select tools
    tools = get_tools_by_names(tool_names)

    # Create system prompt
    system_prompt = apply_prompt_template(
        "dynamic_actor_prompt",
        state,
    )

    # Create agent

    agent = create_agent(model=llm, tools=tools, system_prompt=system_prompt)

    state["messages"].append(HumanMessage(content=current_subtask))

    try:
        result = agent.invoke(
            {"messages": [HumanMessage(content=current_subtask)]})
        print('dynamic_actor_node result', result)

        # Extract the final response
        messages = result.get("messages", [])
        last_message = messages[-1] if messages else None
        content = last_message.content if last_message else "No response"

        return {
            "subtask_result": {
                "status": "success",
                "summary": content,
                "artifacts": []  # Could extract artifacts if needed
            },
            # We might want to append the actor's log to the global history
            # "task_history": state.get("task_history", []) + [f"Subtask: {current_subtask}\nResult: {content}"]
        }
    except Exception as e:
        return {
            "subtask_result": {
                "status": "failed",
                "summary": f"Execution failed: {str(e)}"
            }
        }
