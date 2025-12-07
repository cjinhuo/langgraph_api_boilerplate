import hashlib
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from src.llms.fz import fz_k2_chat_model
from src.tools import search_web, read_url_by_markdown
from src.monitoring import setup_langsmith, get_langsmith_callbacks
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware.todo import TodoListMiddleware
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.types import Command
from src.utils.stream import handle_stream_mode_values
from src.prompts.template import apply_prompt_template
from src.state import State
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_core.output_parsers import JsonOutputParser
# 初始化 LangSmith（如果配置了环境变量会自动启用）
setup_langsmith()

memory = InMemorySaver()


def research_node(state: State):
    research_agent = create_agent(
        model=fz_k2_chat_model,
        tools=[search_web, read_url_by_markdown],
        middleware=[],
        system_prompt=apply_prompt_template("research_prompt", {}),
    )
    user_input_optimized = state.get("user_input_optimized", "")
    result = research_agent.invoke(
        {"messages": [HumanMessage(content=user_input_optimized)]}
    )
    print('research_node result', result)
    return {
        "messages": result["messages"]
    }


def coordinator_node(state: State):
    coordinator_agent = create_agent(
        model=fz_k2_chat_model,
        tools=[],
        middleware=[],
        system_prompt=apply_prompt_template("research_coordinator", {}),
    )
    # 获取用户查询
    user_query = ""
    if state.get("messages"):
        first_msg = state["messages"][0]
        if isinstance(first_msg, dict):
            user_query = first_msg.get("content", "")
        elif hasattr(first_msg, "content"):
            user_query = first_msg.content
    result = coordinator_agent.invoke({
        "messages": [
            HumanMessage(content=user_query)
        ]
    })
    parser = JsonOutputParser()
    print('coordinator_node result', result)
    # 从 result 的 messages 中提取最后一个 AI 消息的内容
    last_message = result["messages"][-1]
    content = last_message.content if isinstance(
        last_message.content, str) else str(last_message.content)
    user_input_optimized = parser.parse(
        text=content).get("user_input_optimized", "")
    return {
        "user_input_optimized": user_input_optimized,
        "messages": result["messages"]
    }


def create_workflow():
    workflow = StateGraph(State)

    workflow.add_node("coordinator", coordinator_node)
    workflow.add_node("research", research_node)

    workflow.add_edge(START, "coordinator")
    workflow.add_edge("coordinator", "research")
    workflow.add_edge("research", END)

    return workflow.compile()


research_agent = create_workflow()

if __name__ == "__main__":
    print("\n开始调用 agent (流式输出)...\n")
    print("=" * 80)
    # 获取 LangSmith 回调（如果已配置）
    callbacks = get_langsmith_callbacks()

    # 创建配置，包含 thread_id 用于 checkpointer
    from langchain_core.runnables import RunnableConfig

    config: RunnableConfig = {
        "configurable": {"thread_id": "research-thread-1"},
    }
    if callbacks:
        config["callbacks"] = callbacks

    # 使用流式输出，使用 values 模式以便检测中断
    input_data = {
        "messages": [
            HumanMessage(content="最新黄金价格")
        ]
    }

    for chunk in research_agent.stream(
        input=input_data,  # type: ignore
        config=config,
        stream_mode=["values"],
    ):
        handle_stream_mode_values(chunk)
