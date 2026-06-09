from mcp.server.fastmcp import FastMCP

# mcp = FastMCP("my-http-mcp-server", port=5555)
mcp = FastMCP("my-http-mcp-server")  # 기본값은 8000 임

@mcp.tool()
def hello(name: str) -> str:
    """ 사용자에게 인사말을 생성하는 도구 

        매개변수:
            name (str): 인사할 대상의 이름

        반환값:
            str: "Hello, {name}!" 형태의 인사말
    """
    return f"Hello, {name}!"

@mcp.tool()
def add(a: int, b: int) -> int:
    """ 두 정수의 덧셈을 수행하는 계산 도구 """
    return a + b

@mcp.tool()
def now() -> str:
    """ 현재 시간을 한국어로 포멧하여 반환하는 도구 """
    from datetime import datetime
    return datetime.now().strftime("지금 시간은 %Y-%m-%d %H:%M:%S 입니다.")


if __name__ == "__main__":
    mcp.run(transport="streamable-http")  # <-- 이거 한줄 한단어로 stdio -> http 서버로 전환
