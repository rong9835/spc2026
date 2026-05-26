# WebSocket 핵심 요약

## WebSocket이 뭔가요?

> **비유로 이해하기**
> - **HTTP** = 편지 → 보내고 → 답장 받고 → **연결 끊김** → 또 보내고...
> - **WebSocket** = 전화 통화 → 한 번 연결하면 → **서로 언제든 실시간으로 대화 가능**

| 구분 | HTTP (기존 방식) | WebSocket |
|------|----------------|-----------|
| 연결 | 요청할 때마다 새로 연결 | 한 번 연결하면 계속 유지 |
| 방향 | 클라이언트 → 서버 (단방향) | 클라이언트 ↔ 서버 (양방향) |
| 속도 | 느림 (매번 핸드셰이크) | 빠름 (연결 유지) |
| 주소 | `http://` | `ws://` |
| 예시 | 웹페이지 로드, REST API | 채팅, 실시간 알림, 게임 |

```
[HTTP]                              [WebSocket]
클라이언트 → "안녕?" → 서버         클라이언트 ↔ 서버  (연결 유지 중)
클라이언트 ← "안녕!" ← 서버              언제든지 서로 메시지 가능!
(연결 끊김)
클라이언트 → "있어?" → 서버   ← 다시 연결해야 해서 비효율적
```

---

## 학습 순서

```
1.intro/        → 순수 WebSocket (websockets 라이브러리)
2.flask_ws/     → Flask + WebSocket (flask-sock 라이브러리)
3.socket_io/    → Socket.IO (더 편리한 고급 버전)
```

---

## 1단계: 순수 WebSocket (`1.intro/`)

### 서버 코드 (`1.server.py`)

```python
import asyncio
import websockets

# 클라이언트가 접속할 때마다 이 함수가 실행됨
async def handle_client(websocket):
    await websocket.send("서버에 연결되었습니다.")   # ① 연결하자마자 인사

    try:
        async for message in websocket:              # ② 메시지가 올 때마다 반복
            print("클라이언트 메시지:", message)
            await websocket.send(f"서버가 받은 메시지: {message}")  # ③ 에코
    except websockets.exceptions.ConnectionClosed:
        print("클라이언트가 연결 종료함.")            # ④ 연결 끊기면 처리

async def main():
    async with websockets.serve(handle_client, "localhost", 8000):
        await asyncio.Future()  # 서버를 계속 켜놓음 (무한 대기)

asyncio.run(main())
```

#### 핵심 키워드

| 키워드 | 의미 |
|--------|------|
| `async def` | 비동기 함수 (여러 클라이언트를 동시에 처리) |
| `await` | "이 작업 끝날 때까지 기다려" |
| `websockets.serve(함수, 주소, 포트)` | WebSocket 서버 시작 |
| `websocket.send()` | 클라이언트에게 메시지 전송 |
| `async for message in websocket` | 클라이언트 메시지를 계속 기다림 |
| `asyncio.Future()` | 서버를 종료하지 않고 계속 실행 |

### 클라이언트 코드 (`1.client.html`)

```javascript
// ① 서버에 WebSocket 연결 요청 (전화 걸기)
const socket = new WebSocket("ws://localhost:8000");

// ② 연결 성공했을 때
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

#### 클라이언트 이벤트 4가지

| 이벤트 | 언제 실행? |
|--------|-----------|
| `socket.onopen` | 서버와 연결 성공했을 때 |
| `socket.onmessage` | 서버에서 메시지 왔을 때 |
| `socket.onclose` | 연결이 끊겼을 때 |
| `socket.onerror` | 에러가 발생했을 때 |

### 전체 흐름

```
브라우저 (client.html)              서버 (server.py)
       │                                  │
       │─── ws://localhost:8000 연결 ────▶│  handle_client() 실행
       │◀── "서버에 연결되었습니다." ──────│
       │                                  │
       │─── "안녕하세요" 전송 ───────────▶│  print("클라이언트 메시지: 안녕하세요")
       │◀── "서버가 받은 메시지: 안녕하세요"│
       │                                  │
       │         (연결 계속 유지...)        │
```

### 실행 방법

```bash
pip install websockets
python 1.server.py
# → 브라우저에서 1.client.html 파일 직접 열기
# → F12 콘솔에서 메시지 확인
```

---

## 2단계: Flask + WebSocket (`2.flask_ws/`)

> Flask 웹서버에 WebSocket 기능을 추가한 버전

### 서버 코드 (`app.py`)

```python
from flask import Flask, send_from_directory
from flask_sock import Sock           # ← WebSocket 라이브러리

app = Flask(__name__)
sock = Sock(app)                      # Flask에 WebSocket 기능 추가

@app.route("/")                       # 일반 HTTP 라우트 (웹페이지)
def index():
    return send_from_directory("static", "index.html")

@sock.route("/ws")                    # WebSocket 라우트 (@sock.route 사용!)
def websocket(ws):
    ws.send("서버에 연결되었습니다.")

    while True:                       # 연결 유지되는 동안 계속 대기
        try:
            message = ws.receive()   # 클라이언트 메시지 기다리기
            ws.send(f"이번에도 이전처럼 메시지 돌려주기: {message}")
        except Exception as e:
            break                    # 연결 끊기면 루프 종료
```

#### `while True`를 쓰는 이유

> WebSocket은 "전화 통화"니까 연결이 유지되는 동안 계속 메시지를 주고받아야 해요.
> 루프가 없으면 함수가 바로 끝나버려서 연결이 끊깁니다!

#### HTTP 라우트 vs WebSocket 라우트 비교

| | HTTP 라우트 | WebSocket 라우트 |
|--|------------|----------------|
| 데코레이터 | `@app.route("/")` | `@sock.route("/ws")` |
| 함수 파라미터 | 없음 | `ws` (연결 객체) |
| 동작 방식 | 요청 1번 → 응답 1번 → 끝 | `while True`로 계속 대기 |
| 연결 | 요청마다 새로 연결 | 계속 유지 |

### 실행 방법

```bash
pip install flask flask-sock
python app.py
# → 브라우저에서 http://localhost:5000 접속
```

---

## 3단계: Socket.IO (`3.socket_io/`)

> WebSocket을 더 쉽고 강력하게 쓸 수 있는 라이브러리

### Socket.IO가 뭔가요?

> WebSocket은 "전화기 회선" 자체라면,
> Socket.IO는 "편리한 스마트폰 앱"이에요.
> 자동 재연결, 이벤트 이름 지정 등 편의 기능이 많아요.

### 서버 코드 (`app.py`)

```python
from flask import Flask, send_from_directory
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my-secret-key'
socketio = SocketIO(app)             # Socket.IO 초기화

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@socketio.on('message')              # 'message' 이벤트가 오면 실행
def handle_message(msg):
    print('Message:', msg)
    send(msg, broadcast=True)        # 모든 접속자에게 전달! (broadcast)

if __name__ == '__main__':
    socketio.run(app, debug=True)    # app.run() 대신 socketio.run() 사용
```

#### 핵심: `broadcast=True`

```
[일반 send]                         [broadcast=True]
    나 → 서버 → 나만 받음                나 → 서버 → 모든 접속자가 받음
                                     (채팅방 기능 구현 가능!)
```

### 클라이언트 코드 (`index.html`)

```javascript
// CDN으로 Socket.IO 라이브러리 로드 (HTML head에 추가 필요)
// <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>

const socket = io();                 // WebSocket과 달리 주소 없이 간단하게!

socket.on('connect', () => {         // 'on'으로 이벤트 구독
    console.log('서버와 연결됨');
});

socket.on('message', (msg) => {      // 'message' 이벤트 수신
    const li = document.createElement('li');
    li.appendChild(document.createTextNode(msg));
    document.getElementById('messages').appendChild(li);  // 화면에 표시
});

document.getElementById('send').addEventListener('click', () => {
    const message = document.getElementById('msg').value;
    socket.send(message);            // 서버로 전송
});
```

### WebSocket vs Socket.IO 비교

| | 순수 WebSocket | Socket.IO |
|--|--------------|-----------|
| 연결 코드 | `new WebSocket("ws://...")` | `io()` |
| 이벤트 방식 | `onmessage`, `onopen` | `socket.on('이벤트명', ...)` |
| 자동 재연결 | ❌ 직접 구현 | ✅ 자동 |
| broadcast | ❌ 직접 구현 | ✅ `broadcast=True` |
| 난이도 | 낮음 | 낮음 (오히려 더 편함) |

### 실행 방법

```bash
pip install flask flask-socketio
python app.py
# → 브라우저에서 http://localhost:5000 접속
# → 탭 2개 열고 메시지 보내면 broadcast 확인 가능
```

---

## 전체 비교 한눈에 보기

| | 1.intro | 2.flask_ws | 3.socket_io |
|--|---------|-----------|------------|
| 라이브러리 | `websockets` | `flask-sock` | `flask-socketio` |
| 서버 실행 | `asyncio.run()` | `app.run()` | `socketio.run()` |
| WebSocket 주소 | `ws://localhost:8000` | `ws://localhost:5000/ws` | 자동 (CDN 사용) |
| 메시지 받기 | `async for message in ws` | `ws.receive()` | `@socketio.on('message')` |
| 메시지 보내기 | `websocket.send()` | `ws.send()` | `send()` |
| 전체 전송 | ❌ | ❌ | ✅ `broadcast=True` |
| 난이도 | 중 | 하 | 하 |

---

## 기억할 핵심 3가지

1. **WebSocket = 전화 통화** → `ws://` 주소, 한 번 연결하면 계속 양방향 통신
2. **서버는 루프로 대기** → `while True` 또는 `async for`로 메시지를 계속 기다림
3. **클라이언트는 이벤트 방식** → `onopen`, `onmessage`, `onclose`로 반응

---

## 실제 활용 예시

| 기능 | 방식 |
|------|------|
| 1:1 채팅 | WebSocket + echo |
| 단체 채팅방 | Socket.IO + broadcast |
| 실시간 주식 가격 | 서버 → 클라이언트 단방향 push |
| 멀티플레이어 게임 | Socket.IO + 커스텀 이벤트 |
| 실시간 알림 | 서버 → 클라이언트 push |
