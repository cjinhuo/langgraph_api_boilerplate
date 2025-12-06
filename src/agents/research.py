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


# 初始化 LangSmith（如果配置了环境变量会自动启用）
setup_langsmith()

memory = InMemorySaver()


research_agent = create_agent(
    model=fz_k2_chat_model,
    tools=[search_web, read_url_by_markdown],  # 添加 todo list 中间件
    middleware=[
        TodoListMiddleware(),
        # HumanInTheLoopMiddleware(
        #     interrupt_on={
        #         "search_web": False,  # 对 search_web 的所有调用进行人工审批
        #         "read_url": False,  # 对 read_url 的所有调用进行人工审批
        #     },
        #     description_prefix="工具执行待审批",
        # ),
    ],
    system_prompt=apply_prompt_template("research_prompt", {}),
    # checkpointer=memory,  # HumanInTheLoopMiddleware 需要 checkpointer
)


if __name__ == "__main__":
    print("\n开始调用 agent (流式输出)...\n")
    print("=" * 80)

    research_agent = create_agent(
        model=fz_k2_chat_model,
        tools=[search_web, read_url_by_markdown],  # 添加 todo list 中间件
        middleware=[
            TodoListMiddleware(),
            HumanInTheLoopMiddleware(
                interrupt_on={
                    "search_web": False,
                    "read_url": False,
                },
                description_prefix="工具执行待审批",
            ),
        ],
        system_prompt="You are a helpful research assistant.",
        checkpointer=memory,  # HumanInTheLoopMiddleware 需要 checkpointer
    )
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
            HumanMessage(content="Research openai and Google models")
        ]
    }

    for chunk in research_agent.stream(
        input=input_data,  # type: ignore
        config=config,
        stream_mode=["values"],
    ):
        handle_stream_mode_values(chunk)
