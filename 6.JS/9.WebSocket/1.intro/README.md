# WebSocket 입문 핵심 요약

## 1. WebSocket이 뭔가요?

> **비유**: 일반 HTTP는 "편지 보내기"고, WebSocket은 "전화 통화"예요.

| 구분 | HTTP (기존 방식) | WebSocket |
|------|----------------|-----------|
| 연결 | 요청할 때마다 새로 연결 | 한 번 연결하면 계속 유지 |
| 방향 | 클라이언트 → 서버 (단방향) | 클라이언트 ↔ 서버 (양방향) |
| 예시 | 웹페이지 로드, REST API | 채팅, 실시간 알림, 게임 |

```
[HTTP]
클라이언트 → "안녕?" → 서버
클라이언트 ← "안녕!" ← 서버  (연결 끊김)
클라이언트 → "있어?" → 서버  (다시 연결해야 함)

[WebSocket]
클라이언트 ↔ 서버  (연결 유지 중)
언제든지 서로 메시지 주고받기 가능!
```

---

## 2. 전체 구조

```
브라우저 (client.html)          서버 (server.py)
       │                              │
       │  ws://localhost:8000 연결 요청 │
       │ ─────────────────────────── ▶│
       │                              │ handle_client() 함수 실행
       │ ◀─────────────────────────── │ "서버에 연결되었습니다." 전송
       │                              │
       │  "안녕하세요" 전송             │
       │ ─────────────────────────── ▶│ print("클라이언트 메시지: 안녕하세요")
       │ ◀─────────────────────────── │ "서버가 받은 메시지: 안녕하세요" 전송
       │                              │
       │  (계속 연결 유지...)           │
```

---

## 3. 서버 코드 분석 (`1.server.py`)

```python
import asyncio
import websockets

# ① 클라이언트가 접속할 때마다 이 함수가 실행됨
async def handle_client(websocket):
    await websocket.send("서버에 연결되었습니다.")  # 연결하자마자 메시지 보냄

    try:
        async for message in websocket:              # 메시지가 올 때마다 반복
            print("클라이언트 메시지:", message)
            await websocket.send(f"서버가 받은 메시지: {message}")  # 에코(echo)
    except websockets.exceptions.ConnectionClosed:
        print("클라이언트가 연결 종료함.")           # 연결 끊기면 예외 처리

# ② 서버 시작
async def main():
    async with websockets.serve(handle_client, "localhost", 8000):
        print("웹소켓을 열었음: ws://localhost:8000")
        await asyncio.Future()  # 서버를 계속 켜놓음 (무한 대기)

asyncio.run(main())
```

### 핵심 키워드

| 키워드 | 의미 |
|--------|------|
| `async def` | 비동기 함수 (여러 클라이언트를 동시에 처리 가능) |
| `await` | "이 작업 끝날 때까지 기다려" |
| `websockets.serve(함수, 주소, 포트)` | WebSocket 서버 시작 |
| `websocket.send()` | 클라이언트에게 메시지 전송 |
| `async for message in websocket` | 클라이언트 메시지를 계속 기다림 |
| `asyncio.Future()` | 서버를 종료하지 않고 계속 실행 |

---

## 4. 클라이언트 코드 분석 (`1.client.html`)

```javascript
// ① 서버에 WebSocket 연결 요청
const socket = new WebSocket("ws://localhost:8000");

// ② 연결이 성공했을 때
socket.onopen = () => {
    console.log("서버와 연결됨.")
}

// ③ 서버에서 메시지가 왔을 때
socket.onmessage = (event) => {
    console.log("서버 메시지: ", event.data);  // event.data에 실제 내용 있음
}

// ④ 버튼 클릭 시 서버에 메시지 전송
document.getElementById('send').addEventListener('click', () => {
    const msg = document.getElementById("msg").value;
    socket.send(msg);  // 서버로 메시지 보내기
})
```

### 클라이언트 이벤트 3가지

```
socket.onopen    → 연결됐을 때 실행
socket.onmessage → 서버에서 메시지 받았을 때 실행
socket.onclose   → 연결이 끊겼을 때 실행 (이 예제엔 없음)
```

---

## 5. 실행 방법

```bash
# 1. 패키지 설치 (처음 한 번만)
pip install websockets

# 2. 서버 실행
python 1.server.py

# 3. 브라우저에서 client.html 열기
#    → F12 콘솔에서 메시지 확인
```

---

## 6. 흐름 요약 (한 눈에 보기)

```
1. python server.py 실행  →  서버 대기 중...

2. 브라우저에서 client.html 열기
   └── new WebSocket("ws://localhost:8000") 실행
   └── 서버의 handle_client() 함수 호출됨

3. 서버 → 클라이언트: "서버에 연결되었습니다."
   └── onmessage 이벤트 발생 → 콘솔에 출력

4. 입력창에 메시지 입력 후 버튼 클릭
   └── socket.send(msg) 실행
   └── 서버의 async for 루프에서 받음

5. 서버 → 클라이언트: "서버가 받은 메시지: xxx"
   └── onmessage 이벤트 발생 → 콘솔에 출력
```

---

## 7. 기억할 포인트

- `ws://` = WebSocket 주소 (http:// 대신 사용)
- WebSocket은 **연결을 유지**하기 때문에 채팅, 실시간 기능에 적합
- 서버는 `async/await`로 여러 클라이언트를 **동시에** 처리
- 클라이언트는 `onopen`, `onmessage` **이벤트 방식**으로 동작
