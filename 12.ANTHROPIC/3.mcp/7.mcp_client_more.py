import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(command="python", args=["6.mcp_server_moretools.py"])

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 너 어떤 도구 있니?
            tools = (await session.list_tools()).tools
            print("도구: ", [t.name for t in tools])

            result = (await session.call_tool("add", {"a": 3, "b": 5})).content[0].text
            print("add도구 호출결과: ", result)

            result = (await session.call_tool("word_count", {"text":"너는 어떤 서버니?"})).content[0].text
            print("word_count 도구 호출결과: ", result)

if __name__ == "__main__":
    asyncio.run(main())
