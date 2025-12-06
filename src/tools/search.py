"""
网络搜索工具
"""
from langchain_core.tools import tool
from langchain.tools import ToolRuntime


@tool("search_web", parse_docstring=True)
def search_web(query: str, runtime: ToolRuntime) -> str:
    """搜索网络信息并返回格式化文本。

    Args:
        query (str): 搜索关键词，不能为空

    Returns:
        str: 带编号的搜索结果列表，每项包含标题、摘要和URL
    """

    # 打印输入信息
    print(f"[search_web] 输入: query={query}")

    try:
        from ddgs import DDGS

        # 使用 DuckDuckGo 搜索
        ddgs = DDGS()
        # ddgs 是代理类，延迟加载 和 按需加载
        # type: ignore[attr-defined]
        results = list(ddgs.text(query, max_results=5))

        if not results:
            output = "未找到搜索结果"
            print(f"[search_web] 输出: {output}")
            return output

        # 格式化搜索结果
        formatted_results = []
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            body = result.get('body', 'No description')
            url = result.get('href', 'No URL')
            formatted_results.append(f"{i}. {title}\n   {body}\n   {url}")

        output = "\n\n".join(formatted_results)
        output_preview = output[:300] + "..." if len(output) > 300 else output
        print(f"[search_web] 输出: {output_preview}")
        return output
    except ImportError:
        output = "Error: ddgs 库未安装。请运行: uv add ddgs"
        print(f"[search_web] 输出: {output}")
        return output
    except Exception as e:
        output = f"搜索出错: {str(e)}"
        print(f"[search_web] 输出: {output}")
        return output
