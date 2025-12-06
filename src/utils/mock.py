from langchain.tools import ToolRuntime


def mock_tool_runtime():
    # 创建一个简单的 mock stream writer
    def mock_stream_writer(content: str) -> None:
        """Mock stream writer for testing"""
        pass

    return ToolRuntime(
        state={},
        context={},
        config={},
        stream_writer=mock_stream_writer,
        tool_call_id=None,
        store=None
    )
