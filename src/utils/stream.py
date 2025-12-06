from langchain_core.messages import AIMessage, AIMessageChunk, ToolMessage, ToolMessageChunk, BaseMessage
from typing import Any, Union


MessageChunkType = Union[AIMessageChunk,
                         AIMessage, ToolMessageChunk, ToolMessage]


def handle_stream_mode_messages(tuple_message: tuple[str, tuple[MessageChunkType, dict[str, Any]]]):
    """
    处理 stream_mode=['messages'] 返回的消息块

    Args:
        tuple_message: 格式为 ('messages', (message_chunk, metadata))
            - message_chunk: AIMessageChunk, AIMessage, ToolMessageChunk 或 ToolMessage
            - metadata: 包含 thread_id, langgraph_step 等信息的字典
    """
    message_type = tuple_message[0]
    tuple_chunk = tuple_message[1]
    chunk = tuple_chunk[0]
    metadata = tuple_chunk[1]
    if isinstance(chunk, AIMessageChunk):
        print(f"AIMessageChunk: {chunk.content}")
    elif isinstance(chunk, AIMessage):
        print(f"AIMessage: {chunk.content}")
    elif isinstance(chunk, ToolMessageChunk):
        print(
            f"ToolMessageChunk: {chunk.name} {chunk.content} {chunk.tool_call_id}")
    elif isinstance(chunk, ToolMessage):
        print(f"ToolMessage: {chunk.name} {chunk.content} ")
    return None


def handle_stream_mode_values(chunk: Any) -> BaseMessage | None:
    """
    处理 stream_mode=['values'] 返回的消息块

    Args:
        chunk: 格式为 (type_name, chunk_data)
            - type_name: 通常是 'values'
            - chunk_data: 包含 messages 等状态信息的字典
    """
    # 使用函数属性维护已处理的消息 ID 集合，避免重复输出
    if not hasattr(handle_stream_mode_values, "seen_message_ids"):
        handle_stream_mode_values.seen_message_ids = set()

    (type_name, chunk_data) = chunk
    if type_name == "values":
        messages = chunk_data.get("messages", []) if isinstance(
            chunk_data, dict) else []
        for message in messages:
            message_id = getattr(message, "id", None)
            if message_id and message_id not in handle_stream_mode_values.seen_message_ids:
                handle_stream_mode_values.seen_message_ids.add(str(message_id))
                print(
                    f"\n[{message.__class__.__name__}] {message.content}")
                return message
