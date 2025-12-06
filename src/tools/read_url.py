"""
网页读取工具
"""
from langchain_core.tools import tool
from langchain.tools import ToolRuntime
from src.utils.mock import mock_tool_runtime

try:
    import requests
except ImportError:
    requests = None

try:
    import trafilatura
except ImportError:
    trafilatura = None


@tool("read_url_by_originally", parse_docstring=True)
def read_url_by_originally(url: str, runtime: ToolRuntime, max_chars: int = 4000) -> str:
    """读取指定网页并返回原始正文文本。

    Args:
        url (str): 需要读取的 http/https 地址，不能为空
        max_chars (int, optional): 截断前的最大字符数，默认 4000

    Returns:
        str: 网页正文文本，如需截断会附带提示信息
    """

    # 打印输入信息
    print(f"[read_url_by_originally] 输入: url={url}, max_chars={max_chars}")

    if not url:
        return "Error: url 不能为空"

    if not isinstance(max_chars, int) or max_chars <= 0:
        return "Error: max_chars 必须是正整数"

    if not url.startswith(("http://", "https://")):
        return "Error: 仅支持 http 或 https 协议"

    if requests is None:
        output = "Error: requests 库未安装。请运行: uv add requests"
        print(f"[read_url_by_originally] 输出: {output}")
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
        print(f"[read_url_by_originally] 输出: {output}")
        return output

    text = response.text.strip()
    if not text:
        output = "读取成功，但页面内容为空"
        print(f"[read_url_by_originally] 输出: {output}")
        return output

    if len(text) <= max_chars:
        output_preview = text[:300] + "..." if len(text) > 300 else text
        print(f"[read_url_by_originally] 输出: {output_preview}")
        return text

    truncated = text[:max_chars].rstrip()
    output = f"{truncated}\n\n... (内容已截断，原文共 {len(text)} 个字符)"
    output_preview = output[:300] + "..." if len(output) > 300 else output
    print(f"[read_url_by_originally] 输出: {output_preview}")
    return output


@tool("read_url_by_markdown", parse_docstring=True)
def read_url_by_markdown(url: str, runtime: ToolRuntime, max_chars: int = 4000) -> str:
    """读取指定网页并返回 Markdown 格式的正文内容。

    使用 trafilatura 库提取网页正文并转换为 Markdown 格式，自动过滤广告、导航等噪音内容。

    Args:
        url (str): 需要读取的 http/https 地址，不能为空
        max_chars (int, optional): 截断前的最大字符数，默认 4000

    Returns:
        str: 网页正文的 Markdown 格式文本，如需截断会附带提示信息
    """

    # 打印输入信息
    print(f"[read_url] 输入: url={url}, max_chars={max_chars}")

    if not url:
        return "Error: url 不能为空"

    if not isinstance(max_chars, int) or max_chars <= 0:
        return "Error: max_chars 必须是正整数"

    if not url.startswith(("http://", "https://")):
        return "Error: 仅支持 http 或 https 协议"

    if requests is None:
        output = "Error: requests 库未安装。请运行: uv add requests"
        print(f"[read_url] 输出: {output}")
        return output

    if trafilatura is None:
        output = "Error: trafilatura 库未安装。请运行: uv add trafilatura"
        print(f"[read_url] 输出: {output}")
        return output

    try:
        # 使用 requests 下载网页内容
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
        downloaded = response.text

        if not downloaded:
            output = "Error: 无法下载网页内容"
            print(f"[read_url] 输出: {output}")
            return output
        print(f"[read_url] 下载的网页内容: {downloaded[:500]}...")

        # 使用 trafilatura 提取网页内容并转换为 Markdown
        markdown_text = trafilatura.extract(
            downloaded,
            output_format="markdown",
            include_comments=False,
            include_tables=True,
            include_images=False,
            include_links=True,
        )

        if not markdown_text or not markdown_text.strip():
            output = "读取成功，但页面内容为空或无法提取正文"
            print(f"[read_url] 输出: {output}")
            return output

        text = markdown_text.strip()

        if len(text) <= max_chars:
            output_preview = text[:300] + "..." if len(text) > 300 else text
            print(f"[read_url] 输出: {output_preview}")
            return text

        truncated = text[:max_chars].rstrip()
        output = f"{truncated}\n\n... (内容已截断，原文共 {len(text)} 个字符)"
        output_preview = output[:300] + "..." if len(output) > 300 else output
        print(f"[read_url] 输出: {output_preview}")
        return output

    except Exception as exc:
        output = f"读取页面失败: {exc}"
        print(f"[read_url] 输出: {output}")
        return output


if __name__ == "__main__":
    # print(read_url_by_originally.invoke({
    #     "url": "https://www.baidu.com",
    #     "runtime": mock_tool_runtime()
    # }))
    print("\n开始调用 read_url_by_markdown...\n")
    print(read_url_by_markdown.invoke({
        "url": "https://www.baidu.com",
        "runtime": mock_tool_runtime()
    }))
