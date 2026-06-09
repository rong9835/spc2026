import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

URL = "http://localhost:8000/mcp"

async def main():
    async with streamablehttp_client(URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 내가 원하는 코드는 여기서부터 시작...
            tools = (await session.list_tools()).tools
            print("도구: ", [t.name for t in tools])

if __name__ == "__main__":
    asyncio.run(main())
