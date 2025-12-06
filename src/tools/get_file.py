from langchain_core.tools import tool
from langchain.tools import ToolRuntime
from src.utils.path import resolve_file_path
from typing import Optional


@tool("get_file", parse_docstring=True)
def get_file(file_path: str, runtime: ToolRuntime) -> str:
    """读取指定文件的文本内容。

    提供简单文件读取能力，适用于展示、分析或复用已生成的文本文件。
    仅支持 UTF-8 文本文件。
    支持相对路径（相对于项目根目录）和绝对路径。

    Args:
        file_path (str): 目标文件路径，支持以下格式：
            - 相对路径：如 "test.py" 或 ".llm_gen/test.py" 或 "subdir/script.py"
            - 绝对路径：如 "/Users/username/projects/my_project/.llm_gen/test.py"

    Returns:
        str: 文件文本内容；失败时返回以 "Error:" 开头的错误信息。
    """

    # 打印输入信息
    print(f"[get_file] 输入: file_path={file_path}")

    # 使用通用路径解析函数
    target_path, error = resolve_file_path(file_path, "get_file")
    if error:
        print(f"[get_file] 输出: {error}")
        return error

    # 此时 target_path 必定不为 None（因为 error 为空）
    assert target_path is not None

    # 读取文件内容（UTF-8 文本）
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            content = f.read()
            output_preview = content[:200] + \
                "..." if len(content) > 200 else content
            print(f"[get_file] 输出: {output_preview}")
            return content
    except FileNotFoundError:
        output = f"Error: 文件不存在 {target_path}"
        print(f"[get_file] 输出: {output}")
        return output
    except UnicodeDecodeError:
        output = f"Error: 文件不是 UTF-8 文本或解码失败: {target_path}"
        print(f"[get_file] 输出: {output}")
        return output
    except PermissionError:
        output = f"Error: 没有权限读取文件 {target_path}"
        print(f"[get_file] 输出: {output}")
        return output
    except OSError as e:
        output = f"Error: 文件读取失败: {str(e)}"
        print(f"[get_file] 输出: {output}")
        return output
    except Exception as e:
        output = f"Error: 发生未知错误: {str(e)}"
        print(f"[get_file] 输出: {output}")
        return output
