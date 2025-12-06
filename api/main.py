from fastapi.middleware.cors import CORSMiddleware
from typing import Union, AsyncGenerator, Any, Dict, Optional
import json
import asyncio
import uuid
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn

# 导入 agent 相关模块
from src.agents.research import research_agent
from src.monitoring import get_langsmith_callbacks
from langchain_core.messages import BaseMessage, AIMessage
from langgraph.types import Command
from langchain_core.runnables import RunnableConfig

app = FastAPI(
    title="Agent Research API",
    description="与 LangGraph Agent 进行流式通信的 API",
    version="1.0.0"
)

# 内存存储：用于保存中断状态
# key: thread_id, value: {interrupt_data, action_requests, created_at}
interrupt_storage: Dict[str, Dict[str, Any]] = {}


@app.get("/")
@app.post("/")
def read_root():
    return {
        "message": "Agent Research API",
        "endpoints": {
            "stream": "/stream/chat - 流式聊天接口",
            "docs": "/docs - API 文档"
        }
    }


@app.get("/health")
def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "agent-research-api"}


class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None


@app.post("/stream/chat")
async def stream_chat(body: ChatRequest) -> StreamingResponse:
    """
    流式聊天接口 - 使用 SSE (Server-Sent Events) 格式，支持中断检测

    Args:
        message: 用户输入的消息（如果是恢复执行，可以为空）
        thread_id: 可选的 thread_id，用于恢复对话或创建新对话

    Returns:
        StreamingResponse: SSE 格式的流式响应

    事件类型:
        - "message": 正常消息内容
        - "interrupt": 中断事件，需要前端调用 /resume 端点恢复
        - "error": 错误信息
        - "done": 流结束

    前端使用示例:
        const response = await fetch('/stream/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ message: 'Hello', thread_id: 'thread-123' })
        });
        const reader = response.body.getReader();
        // 处理流式数据...
    """

    async def generate_stream() -> AsyncGenerator[str, None]:
        """
        生成 SSE 格式的流式响应，支持中断检测和恢复
        """
        try:
            # 生成或使用提供的 thread_id
            thread_id = body.thread_id or f"thread-{uuid.uuid4().hex[:8]}"

            # 获取 LangSmith 回调（如果已配置）
            callbacks = get_langsmith_callbacks()

            # 创建配置，包含 thread_id 用于 checkpointer
            config: RunnableConfig = {
                "configurable": {"thread_id": thread_id},
            }
            if callbacks:
                config["callbacks"] = callbacks

            # 判断是恢复执行还是新对话
            if body.thread_id and body.thread_id in interrupt_storage:
                # 恢复执行：使用 Command
                interrupt_info = interrupt_storage[body.thread_id]
                decisions = interrupt_info.get("decisions", [])

                # 发送恢复通知
                resume_data = {
                    "type": "resume",
                    "thread_id": thread_id,
                    "message": "正在恢复执行...",
                }
                json_data = json.dumps(resume_data, ensure_ascii=False)
                yield f"data: {json_data}\n\n"

                # 使用 Command 恢复执行
                current_input: Union[dict, Command] = Command(
                    resume={"decisions": decisions})

                # 清理中断存储
                del interrupt_storage[body.thread_id]
            else:
                # 新对话：使用消息
                current_input = {
                    "messages": [
                        {"role": "user", "content": body.message}
                    ]
                }

            # 使用 values 模式以便检测中断
            astream = research_agent.astream(
                current_input,  # type: ignore
                config=config,
                stream_mode="values",  # 使用 values 模式以便检测中断
            )

            async for chunk in astream:
                # 检查是否有中断
                if "__interrupt__" in chunk:
                    interrupt_data = chunk["__interrupt__"]

                    # 提取 action_requests
                    action_requests = []
                    if interrupt_data:
                        for interrupt in interrupt_data:
                            if hasattr(interrupt, "value") and "action_requests" in interrupt.value:
                                requests = interrupt.value["action_requests"]
                                for request in requests:
                                    action_requests.append({
                                        "request_id": getattr(request, "request_id", None),
                                        "tool_name": getattr(request, "tool_name", None),
                                        "args": getattr(request, "args", {}),
                                        "description": getattr(request, "description", ""),
                                    })

                    # 保存中断状态
                    interrupt_storage[thread_id] = {
                        "interrupt_data": str(interrupt_data),  # 序列化保存
                        "action_requests": action_requests,
                        "created_at": datetime.now().isoformat(),
                    }

                    # 发送中断事件给前端
                    interrupt_event = {
                        "type": "interrupt",
                        "thread_id": thread_id,
                        "action_requests": action_requests,
                        "message": "检测到中断，需要人工审批",
                    }
                    json_data = json.dumps(interrupt_event, ensure_ascii=False)
                    yield f"data: {json_data}\n\n"

                    # 中断后停止流
                    break

                # 处理正常输出
                for node_name, node_output in chunk.items():
                    if node_name == "__interrupt__":
                        continue

                    # 提取消息内容
                    if "messages" in node_output:
                        messages = node_output["messages"]
                        for msg in messages:
                            if isinstance(msg, BaseMessage):
                                content = ""
                                if hasattr(msg, "content") and msg.content:
                                    if isinstance(msg.content, str):
                                        content = msg.content
                                    else:
                                        content = str(msg.content)

                                # 只有当有内容时才发送
                                if content:
                                    chunk_data = {
                                        "type": "message",
                                        "content": content,
                                        "node": node_name,
                                    }
                                    json_data = json.dumps(
                                        chunk_data, ensure_ascii=False)
                                    yield f"data: {json_data}\n\n"

        except Exception as e:
            # 错误处理：发送错误信息给前端
            error_data = {
                "type": "error",
                "message": str(e),
            }
            json_data = json.dumps(error_data, ensure_ascii=False)
            yield f"data: {json_data}\n\n"
        finally:
            # 发送结束标记
            done_data = {
                "type": "done",
                "message": "流结束",
            }
            json_data = json.dumps(done_data, ensure_ascii=False)
            yield f"data: {json_data}\n\n"

    # 返回流式响应 - 使用 text/event-stream 作为 SSE 格式
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

# 添加 CORS 支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
