"""
MCP 服务器主入口
"""
from mcp.server.fastmcp import FastMCP

# 创建 FastMCP 实例
mcp = FastMCP("misc-mcp")

# 导入所有工具模块（这会自动注册所有工具）
from misc_mcp.tools import base64_tools


def main():
    """启动 MCP 服务器"""
    mcp.run()


if __name__ == "__main__":
    main()

