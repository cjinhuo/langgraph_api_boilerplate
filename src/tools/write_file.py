"""
文件写入工具
"""
from langchain_core.tools import tool
from langchain.tools import ToolRuntime
from typing import Optional
from src.utils.path import resolve_file_path, get_project_root


@tool("write_file", parse_docstring=True)
def write_file(file_path: str, content: str, runtime: ToolRuntime) -> str:
    """将内容写入到本地文件系统中的指定文件。

    如果文件路径中包含目录，会自动创建所需的目录结构。
    支持相对路径（相对于项目根目录）和绝对路径。

    Args:
        file_path (str): 文件路径，支持以下格式：
            - 相对路径：如 "test.py" 或 ".llm_gen/test.py" 或 "subdir/script.py"
            - 绝对路径：如 "/Users/username/projects/my_project/.llm_gen/test.py"
        content (str): 要写入文件的内容

    Returns:
        str: 成功时返回文件路径和写入状态，失败时返回错误信息
    """
    # 打印输入信息
    print(
        f"[write_file] 输入: file_path={file_path}, content_length={len(content)}")

    if not isinstance(content, str):
        return "Error: content 必须是字符串类型"

    # 使用通用路径解析函数
    target_path, error = resolve_file_path(file_path, "write_file")
    if error:
        print(f"[write_file] 输出: {error}")
        return error

    # 此时 target_path 必定不为 None（因为 error 为空）
    assert target_path is not None

    # 获取项目根目录（用于显示相对路径）
    project_root = get_project_root()

    try:
        # 创建目录（如果不存在）
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # 写入文件
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)

        # 返回成功信息
        file_size = len(content.encode("utf-8"))
        try:
            # 尝试显示相对于项目根目录的路径
            relative_path = target_path.relative_to(project_root)
            output = f"✅ 文件写入成功: {relative_path}\n文件大小: {file_size} 字节"
        except ValueError:
            # 如果无法计算相对路径（绝对路径在项目外），显示绝对路径
            output = f"✅ 文件写入成功: {target_path}\n文件大小: {file_size} 字节"
        print(f"[write_file] 输出: {output}")
        return output

    except PermissionError:
        output = f"Error: 没有权限写入文件 {target_path}"
        print(f"[write_file] 输出: {output}")
        return output
    except OSError as e:
        output = f"Error: 文件写入失败: {str(e)}"
        print(f"[write_file] 输出: {output}")
        return output
    except Exception as e:
        output = f"Error: 发生未知错误: {str(e)}"
        print(f"[write_file] 输出: {output}")
        return output


if __name__ == "__main__":
    # 测试写入文件
    result = write_file.invoke({
        "file_path": "test_write.py",
        "content": "# Test file\nprint('Hello, World!')"
    })
    print(result)
