"""
工具模块初始化
所有工具模块都会在这里被导入和注册
"""

# 导入编码解码工具集
from .encoding import base64_tools

# 导入取证分析工具集
from .forensics import string_search_tools

__all__ = ['base64_tools', 'string_search_tools']

