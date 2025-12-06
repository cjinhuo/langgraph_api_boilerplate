from pathlib import Path
from typing import Tuple, Optional


def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent


def get_llm_gen_dir() -> Path:
    return get_project_root() / ".llm_gen"


def resolve_file_path(file_path: str, tool_name: str = "tool") -> Tuple[Optional[Path], str]:
    """解析文件路径，支持绝对路径和相对路径（相对于项目根目录）。

    统一处理路径解析、规范化和安全检查逻辑，供各工具函数复用。

    Args:
        file_path (str): 文件路径，支持以下格式：
            - 相对路径：如 "test.py" 或 ".llm_gen/test.py" 或 "subdir/script.py"
            - 绝对路径：如 "/Users/username/projects/my_project/.llm_gen/test.py"
        tool_name (str): 调用工具的名称，用于日志输出

    Returns:
        Tuple[Optional[Path], str]: 
            - 成功时返回 (resolved_path, "")，resolved_path 是规范化后的绝对路径
            - 失败时返回 (None, error_message)，error_message 以 "Error:" 开头

    安全策略：
        - 相对路径必须在项目根目录内，否则返回错误
        - 绝对路径允许在项目根目录外，但会打印警告
        - 自动处理路径中的 .. 和 . 符号
    """
    if not file_path:
        return None, "Error: file_path 不能为空"

    project_root = get_project_root()

    try:
        input_path = Path(file_path)

        if input_path.is_absolute():
            # 绝对路径：直接使用
            target_path = input_path
        else:
            # 相对路径：相对于项目根目录
            # 规范化路径，移除前导斜杠，但保留路径中的点（如 .llm_gen）
            normalized_path = file_path.lstrip("/")
            if not normalized_path:
                return None, "Error: file_path 不能为空或仅为斜杠"
            target_path = project_root / normalized_path

        # 解析并规范化路径（处理 .. 和 . 等符号）
        resolved_path = target_path.resolve()
        resolved_project_root = project_root.resolve()

        # 安全检查：确保路径在项目根目录内（防止访问系统关键目录）
        try:
            resolved_path.relative_to(resolved_project_root)
        except ValueError:
            # 如果不在项目根目录内，检查是否为绝对路径且用户明确指定
            # 对于绝对路径，允许访问，但给出警告提示
            if input_path.is_absolute():
                print(f"[{tool_name}] 警告: 访问项目根目录外的绝对路径: {resolved_path}")
            else:
                return None, f"Error: 文件路径必须在项目根目录内: {project_root}"

        return resolved_path, ""

    except Exception as e:
        return None, f"Error: 解析文件路径失败: {str(e)}"
