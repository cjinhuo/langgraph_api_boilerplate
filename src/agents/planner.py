from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from src.state import State
from src.prompts.template import apply_prompt_template
from src.llms.fz import fz_k2_chat_model

# Initialize LLM
llm = fz_k2_chat_model


def planner_node(state: State):
    """
    The Planner Node (The Brain).
    Analyzes progress and decides the next step.

    首次调用时，只传递 user_input (objective)。
    后续调用时，传递 user_input + progress_list + subtask_result。
    """
    # 提取用户目标 (从消息列表的第一条消息中)
    user_input = "No objective provided."
    if state.get("messages"):
        first_msg = state["messages"][0]
        if isinstance(first_msg, dict):
            user_input = first_msg.get("content", "No content")
        elif hasattr(first_msg, "content"):
            user_input = first_msg.content

    # 判断是否为首次调用
    is_first_run = not state.get('progress_list')

    # 构建消息列表
    messages = [
        SystemMessage(content=apply_prompt_template("planner_prompt", state)),
        HumanMessage(content=f"Objective: {user_input}")
    ]

    # 如果不是首次调用，则添加进度列表和子任务结果
    if not is_first_run:
        messages.append(
            HumanMessage(
                content=f"Current Progress List:\n{state.get('progress_list', 'No plan yet.')}")
        )
        messages.append(
            HumanMessage(
                content=f"Last Subtask Result:\n{state.get('subtask_result', 'None')}")
        )

    parser = JsonOutputParser()
    chain = llm | parser

    try:
        result = chain.invoke(messages)
        print(
            f"[Planner] {'Initial' if is_first_run else 'Update'} planning result:", result)
        return {
            "progress_list": result.get("progress_list"),
            "current_subtask": result.get("current_subtask"),
            # 存储 next_action 以便在图中决定何时停止
            # 目前依赖 current_subtask 为 None 或特定标志
        }
    except Exception as e:
        print(f"[Planner] Error: {e}")
        # 错误处理
        return {}
