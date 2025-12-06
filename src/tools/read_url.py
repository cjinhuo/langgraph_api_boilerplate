"""
网页读取工具
"""
from langchain_core.tools import tool
from langchain.tools import ToolRuntime


@tool("read_url", parse_docstring=True)
def read_url(url: str, runtime: ToolRuntime, max_chars: int = 4000) -> str:
    """读取指定网页并返回正文文本。

    Args:
        url (str): 需要读取的 http/https 地址，不能为空
        max_chars (int, optional): 截断前的最大字符数，默认 2000

    Returns:
        str: 网页正文文本，如需截断会附带提示信息
    """

    # 打印输入信息
    print(f"[read_url] 输入: url={url}, max_chars={max_chars}")

    if not url:
        return "Error: url 不能为空"

    if not isinstance(max_chars, int) or max_chars <= 0:
        return "Error: max_chars 必须是正整数"

    if not url.startswith(("http://", "https://")):
        return "Error: 仅支持 http 或 https 协议"

    try:
        import requests
    except ImportError:
        output = "Error: requests 库未安装。请运行: uv add requests"
        print(f"[read_url] 输出: {output}")
        return output

    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/118.0.0.0 Safari/537.36"
                )
            },
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        output = f"读取页面失败: {exc}"
        print(f"[read_url] 输出: {output}")
        return output

    text = response.text.strip()
    if not text:
        output = "读取成功，但页面内容为空"
        print(f"[read_url] 输出: {output}")
        return output

    if len(text) <= max_chars:
        output_preview = text[:300] + "..." if len(text) > 300 else text
        print(f"[read_url] 输出: {output_preview}")
        return text

    truncated = text[:max_chars].rstrip()
    output = f"{truncated}\n\n... (内容已截断，原文共 {len(text)} 个字符)"
    output_preview = output[:300] + "..." if len(output) > 300 else output
    print(f"[read_url] 输出: {output_preview}")
    return output
