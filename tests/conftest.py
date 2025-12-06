"""
Pytest 配置文件
自动设置 Python 路径，使测试能够导入项目模块
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
