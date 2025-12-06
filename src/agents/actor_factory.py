from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from src.state import State
from src.prompts.template import apply_prompt_template
from src.llms.fz import fz_k2_chat_model

# Initialize LLM
llm = fz_k2_chat_model


def actor_factory_node(state: State):
    """
    The Actor Factory Node (The Builder).
    Creates a persona and selects tools for the current subtask.
    """
    current_subtask = state.get("current_subtask")
    if not current_subtask:
        return {}

    messages = [
        SystemMessage(content=apply_prompt_template(
            "actor_factory_prompt", state)),
        HumanMessage(content=f"Current Subtask: {current_subtask}")
    ]

    parser = JsonOutputParser()
    chain = llm | parser

    try:
        result = chain.invoke(messages)
        print('actor_factory_node result', result)

        return {
            "actor_persona": result.get("actor_persona"),
            "actor_tools": result.get("actor_tools")
        }
    except Exception as e:
        print(f"Actor Factory Error: {e}")
        return {}
