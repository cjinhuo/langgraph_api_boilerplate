"""
网页读取工具的单元测试
"""
from src.utils.mock import mock_tool_runtime
from src.tools.read_url import read_url_by_originally
from unittest.mock import Mock, patch


def test_read_url_success():
    """测试成功读取网页"""
    url = "https://www.baidu.com"
    runtime = mock_tool_runtime()

    # Mock requests.get 返回成功响应
    mock_response = Mock()
    mock_response.text = "这是百度首页的内容" * 100  # 模拟网页内容
    mock_response.raise_for_status = Mock()

    with patch("src.tools.read_url.requests.get", return_value=mock_response):
        result = read_url_by_originally.invoke({
            "url": url,
            "runtime": runtime,
            "max_chars": 4000
        })

        assert isinstance(result, str)
        assert len(result) > 0
        assert "Error" not in result
        assert "这是百度首页的内容" in result
