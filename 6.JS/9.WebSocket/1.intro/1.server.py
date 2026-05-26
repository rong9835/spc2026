# pip install websockets
import asyncio
import websockets

# 클라이언트가 요청하면 부를 함수
async def handle_client(websocket):
    print("이 함수 호출: 웹소켓 요청이 올때마다 불림")
    await websocket.send("서버에 연결되었습니다.")

    try:
        async for message in websocket:
            print("클라이언트 메시지:", message)
            await websocket.send(f"서버가 받은 메시지: {message}")
    except websockets.exceptions.ConnectionClosed:
        print("클라이언트가 연결 종료함.")

async def main():
    print("메인 함수")
    async with websockets.serve(handle_client, "localhost", 8000):
        print("웹소켓을 열었음: ws://localhost:8000")
        await asyncio.Future()  # 요청이 올때까지 기다림

asyncio.run(main())
