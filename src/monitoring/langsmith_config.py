"""
LangSmith 配置和追踪设置
"""
import os
from typing import Optional, List
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.tracers import LangChainTracer


# LangSmith 配置应从环境变量读取，不要硬编码密钥
LANGSMITH_ENDPOINT = "https://api.smith.langchain.com"
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "default-project")


def setup_langsmith(
    api_key: Optional[str] = None,
    project: Optional[str] = None,
    api_url: Optional[str] = None,
) -> bool:
    """设置 LangSmith 环境变量

    Args:
        api_key: LangSmith API Key（如果不提供，会从环境变量 LANGSMITH_API_KEY 读取）
        project: 项目名称（如果不提供，会从环境变量 LANGSMITH_PROJECT 读取）
        api_url: LangSmith API URL（可选，默认使用官方地址）

    Returns:
        bool: 是否成功设置

    Example:
        >>> # 方式1: 使用环境变量
        >>> import os
        >>> os.environ["LANGSMITH_API_KEY"] = "your-api-key"
        >>> os.environ["LANGSMITH_PROJECT"] = "my-project"
        >>> setup_langsmith()

        >>> # 方式2: 直接传入参数
        >>> setup_langsmith(api_key="your-api-key", project="my-project")
    """
    # 从参数或环境变量获取配置
    api_key = api_key or os.getenv("LANGSMITH_API_KEY")
    project = project or os.getenv("LANGSMITH_PROJECT", LANGSMITH_PROJECT)
    api_url = api_url or os.getenv("LANGSMITH_ENDPOINT", LANGSMITH_ENDPOINT)

    if not api_key:
        print("⚠️  警告: 未设置 LANGSMITH_API_KEY，LangSmith 追踪将被禁用")
        print("   请设置环境变量 LANGSMITH_API_KEY 或传入 api_key 参数")
        return False

    # 设置环境变量
    os.environ["LANGSMITH_API_KEY"] = api_key
    if project:
        os.environ["LANGSMITH_PROJECT"] = project
    if api_url:
        os.environ["LANGCHAIN_API_URL"] = api_url

    # 启用追踪
    os.environ["LANGCHAIN_TRACING_V2"] = "true"

    print(f"✅ LangSmith 已配置")
    if project:
        print(f"   项目: {project}")
    print(f"   API Key: {api_key[:8]}...")

    return True


def get_langsmith_callbacks(
    project: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> List[BaseCallbackHandler]:
    """获取 LangSmith 回调处理器

    Args:
        project: 项目名称（覆盖环境变量中的设置）
        tags: 标签列表，用于在 LangSmith 中过滤和分类

    Returns:
        List[BaseCallbackHandler]: LangSmith 回调处理器列表

    Example:
        >>> callbacks = get_langsmith_callbacks(project="my-project", tags=["production", "v1"])
        >>> agent.invoke(input, config={"callbacks": callbacks})
    """
    # 检查是否已配置
    if not os.getenv("LANGSMITH_API_KEY"):
        print("⚠️  警告: LANGSMITH_API_KEY 未设置，返回空回调列表")
        return []

    # 使用 LangChainTracer
    tracer = LangChainTracer(
        project_name=project or os.getenv("LANGSMITH_PROJECT", "default"),
        tags=tags or [],
    )

    return [tracer]
