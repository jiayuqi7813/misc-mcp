"""
Base64 编解码工具
提供 Base64 的编码和解码功能
"""
import base64
from misc_mcp.server import mcp


@mcp.tool()
def encode_base64(text: str) -> str:
    """
    将明文字符串编码为 Base64 文本
    
    Args:
        text: 要编码的明文字符串
        
    Returns:
        Base64 编码后的字符串
    """
    try:
        text_bytes = text.encode('utf-8')
        base64_bytes = base64.b64encode(text_bytes)
        base64_string = base64_bytes.decode('utf-8')
        return base64_string
    except Exception as e:
        return f"编码失败: {str(e)}"


@mcp.tool()
def decode_base64(base64_text: str) -> str:
    """
    将 Base64 文本解码为 UTF-8 字符串
    
    Args:
        base64_text: Base64 编码的字符串
        
    Returns:
        解码后的明文字符串
    """
    try:
        base64_bytes = base64_text.encode('utf-8')
        text_bytes = base64.b64decode(base64_bytes)
        text = text_bytes.decode('utf-8')
        return text
    except Exception as e:
        return f"解码失败: {str(e)}"

