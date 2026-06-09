from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hello")

@mcp.tool()
async def hello(name: str) -> str:
    """ 간단한 인사말을 돌려줍니다. """
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
