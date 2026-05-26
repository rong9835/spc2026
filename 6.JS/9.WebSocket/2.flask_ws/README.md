# Flask WebSocket 핵심 요약

## WebSocket이 뭔가요?

> **비유:** 일반 HTTP는 "편지 주고받기"입니다.  
> 보내고 → 답장 받고 → 연결 끊김 → 또 보내고 → 또 받고...  
>
> **WebSocket은 "전화 통화"입니다.**  
> 한 번 연결하면 → 서로 언제든지 실시간으로 말할 수 있음 → 끊을 때만 연결 종료

---

## 이 프로젝트 구조

```
2.flask_ws/
├── app.py              # 서버 (Flask)
└── static/
    └── index.html      # 클라이언트 (브라우저)
```

---

## 서버 코드 분석 (`app.py`)

```python
# pip install flask-sock
from flask import Flask, send_from_directory
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)         # Flask에 WebSocket 기능 추가
```

### 일반 HTTP 라우트 (평범한 웹 페이지)

```python
@app.route("/")
def index():
    return send_from_directory("static", "index.html")
```

- 브라우저가 `http://localhost:5000/` 접속하면 → `index.html` 반환

---

### WebSocket 라우트 (핵심!)

```python
@sock.route("/ws")          # ← @app.route 대신 @sock.route 사용
def websocket(ws):
    ws.send("서버에 연결되었습니다.")   # 연결하자마자 메시지 전송

    while True:             # ← 연결이 유지되는 동안 계속 대기
        try:
            message = ws.receive()      # 클라이언트 메시지 기다리기
            ws.send(f"이번에도 이전처럼 메시지 돌려주기: {message}")  # 에코
        except Exception as e:
            break           # 연결 끊기면 루프 종료
```

| 메서드 | 역할 |
|--------|------|
| `ws.send(메시지)` | 클라이언트에게 메시지 **보내기** |
| `ws.receive()` | 클라이언트 메시지 **받기** (올 때까지 대기) |

> **`while True` 왜 쓰나요?**  
> WebSocket은 "전화 통화"니까 연결이 유지되는 동안 계속 메시지를 주고받아야 합니다.  
> 루프가 없으면 함수가 끝나버려서 연결이 끊겨요!

---

## 클라이언트 코드 분석 (`index.html`)

```javascript
// 1. WebSocket 연결 (전화 걸기)
const socket = new WebSocket("ws://localhost:5000/ws");
//                            ↑ http:// 가 아닌 ws:// 사용!

// 2. 연결됐을 때
socket.onopen = () => {
    console.log("서버와 연결됨.")
}

// 3. 서버에서 메시지 왔을 때
socket.onmessage = (event) => {
    console.log("서버 메시지: ", event.data);  // event.data에 내용 있음
}

// 4. 버튼 클릭 → 메시지 보내기
document.getElementById('send').addEventListener('click', () => {
    const msg = document.getElementById("msg").value;
    socket.send(msg);   // 서버에 전송
})
```

### WebSocket 이벤트 4가지

| 이벤트 | 언제 실행? |
|--------|-----------|
| `socket.onopen` | 서버와 연결 성공했을 때 |
| `socket.onmessage` | 서버에서 메시지 왔을 때 |
| `socket.onclose` | 연결이 끊겼을 때 |
| `socket.onerror` | 에러가 발생했을 때 |

> 이 코드에서는 `onopen`과 `onmessage`만 구현했어요.

---

## 전체 흐름 그림

```
[브라우저]                          [Flask 서버]
    |                                    |
    |--- ws://localhost:5000/ws 접속 --->|  연결 시작
    |                                    |
    |<-- "서버에 연결되었습니다." --------|  서버가 먼저 인사
    |                                    |
    |--- "안녕!" (버튼 클릭) ----------->|  클라이언트 전송
    |                                    |
    |<-- "이번에도 이전처럼 메시지       |  서버가 에코
    |     돌려주기: 안녕!" -------------|
    |                                    |
    |--- "잘가!" --------------------->  |
    |<-- "이번에도... 잘가!" ----------- |
    |                                    |
    |--- 창 닫기 ---------------------->|  연결 종료
    |                                    |  (break로 루프 탈출)
```

---

## HTTP vs WebSocket 비교

| | HTTP | WebSocket |
|--|------|-----------|
| **연결** | 요청마다 새로 연결 | 한 번 연결 후 유지 |
| **통신 방향** | 클라이언트만 먼저 요청 | 양방향 (서버도 먼저 보낼 수 있음) |
| **속도** | 느림 (매번 핸드셰이크) | 빠름 (연결 유지) |
| **사용 예** | 일반 웹페이지 조회 | 채팅, 주식, 게임 |
| **주소 형식** | `http://` | `ws://` |

---

## 실행 방법

```bash
# 1. 라이브러리 설치
pip install flask flask-sock

# 2. 서버 실행
python app.py

# 3. 브라우저에서 접속
# http://localhost:5000 열기
# 개발자 도구(F12) → Console 탭에서 메시지 확인
```

---

## 핵심 정리 3줄

1. **WebSocket = 전화 통화** → 한 번 연결하면 서로 언제든 실시간 메시지 가능
2. **서버**: `@sock.route` + `while True` + `ws.send/receive`
3. **클라이언트**: `new WebSocket("ws://...")` + `onopen/onmessage/send`
