# Flask SSE (Server-Sent Events) 핵심 요약

## SSE가 뭔가요?

> **비유**: 라디오 방송국처럼, **서버가 일방적으로 클라이언트에게 데이터를 밀어줌**

| 방식 | 설명 | 방향 |
|------|------|------|
| 일반 HTTP 요청 | 클라이언트가 물어봐야 서버가 답함 | 클라이언트 → 서버 → 클라이언트 |
| **SSE** | 서버가 먼저, 계속, 알아서 데이터를 보냄 | 서버 → 클라이언트 (단방향) |
| WebSocket | 양방향 실시간 통신 | 클라이언트 ↔ 서버 |

---

## 전체 동작 흐름

```
[브라우저]                          [Flask 서버]
    |                                    |
    |-- GET /stream  (SSE 연결 시작) --> |  ← 브라우저가 채널 열기
    |                                    |
    |<-- "서버에 연결되었습니다!" -------|  ← 서버가 즉시 환영 메시지
    |                                    |
    |   ... 계속 연결 유지 중 ...        |
    |                                    |
    |-- POST /send (메시지 전송) ------> |  ← 사용자가 메시지 보냄
    |                                    |
    |<-- "서버가 받은 메시지: 안녕" -----|  ← 서버가 SSE로 답장
```

---

## 서버 코드 (`app.py`) 분석

### 1. 연결된 사용자 목록 관리

```python
clients = []  # 현재 SSE로 연결된 모든 사용자의 큐(대기열)를 담아두는 리스트
```

> **비유**: 라디오 청취자 명단. 새 사람이 접속하면 추가, 나가면 삭제.

---

### 2. SSE 스트림 API (`/stream`)

```python
@app.route("/stream")
def stream():
    def event_stream():
        q = Queue()           # 이 사용자 전용 메시지 대기열 생성
        clients.append(q)     # 전체 사용자 목록에 추가

        yield f"data: 서버에 연결되었습니다!\n\n"  # 즉시 환영 메시지 전송

        while True:
            message = q.get()   # 메시지가 올 때까지 기다림 (블로킹)
            if message is None:
                break
            yield f"data: {message}\n\n"  # 메시지를 SSE 형식으로 전송

    return Response(event_stream(), mimetype="text/event-stream")
```

#### 핵심 포인트

| 키워드 | 역할 |
|--------|------|
| `Queue()` | 사용자별 메시지 대기열. 메시지가 쌓이면 꺼내서 전송 |
| `yield` | 데이터를 한 번에 보내지 않고 조금씩 스트리밍 |
| `data: ...\n\n` | SSE **웹 표준 형식** — 반드시 `data:` 로 시작, `\n\n` 으로 끝 |
| `mimetype="text/event-stream"` | 브라우저에게 "이건 SSE야!" 라고 알려주는 헤더 |

#### SSE 메시지 형식

```
data: 여기에 보낼 내용\n\n
```

> **주의**: 줄바꿈이 **두 번**(`\n\n`)이어야 브라우저가 한 개의 메시지로 인식함

---

### 3. 메시지 수신 API (`/send`)

```python
@app.route("/send", methods=["POST"])
def send():
    message = request.form.get("msg", "")
    for q in clients:              # 연결된 모든 사용자에게
        q.put(f"서버가 받은 메시지: {message}")  # 메시지를 큐에 넣음
    return ("", 204)               # 204 = 성공했지만 응답 본문 없음
```

> 메시지를 큐에 넣으면 → `/stream`의 `q.get()`이 감지 → SSE로 전송됨

---

## 클라이언트 코드 (`index.html`) 분석

### 1. SSE 연결 시작

```javascript
const source = new EventSource("/stream");  // SSE 채널 열기
```

> **비유**: TV를 켜서 특정 채널에 맞추는 것

### 2. 연결 성공 & 메시지 수신

```javascript
source.onopen = () => {
    console.log("서버와 연결됨");
}

source.onmessage = (event) => {
    console.log("서버 메시지: ", event.data);  // event.data에 내용이 들어있음

    const newReply = document.createElement('div');
    newReply.textContent = event.data;
    reply.appendChild(newReply);  // 화면에 출력
}
```

### 3. 메시지 전송 (일반 fetch POST)

```javascript
fetch("/send", {
    method: 'POST',
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: "msg=" + encodeURIComponent(msg)  // 폼 데이터 형식으로 전송
})
```

> SSE는 **받기만** 함. 보낼 때는 별도로 일반 HTTP POST 사용!

---

## 전체 데이터 흐름 (쉽게)

```
① 브라우저가 /stream 에 연결
        ↓
② 서버: Queue 하나 만들어서 clients 리스트에 추가
        ↓
③ 서버: "연결됐어요!" 메시지 즉시 전송 (yield)
        ↓
④ while True 루프로 대기 중...
        ↓
⑤ 사용자가 /send 로 POST 요청
        ↓
⑥ 서버: 모든 clients의 Queue에 메시지 put()
        ↓
⑦ ④의 q.get()이 깨어남 → yield로 SSE 전송
        ↓
⑧ 브라우저의 onmessage 이벤트 발생 → 화면에 출력
```

---

## 핵심 개념 정리

| 개념 | 설명 |
|------|------|
| `Queue` | 선착순 대기열 (FIFO). `put()`으로 넣고 `get()`으로 꺼냄 |
| `yield` | 함수를 중단하지 않고 값을 하나씩 내보내는 파이썬 키워드 |
| `clients` | 연결된 모든 사용자의 Queue를 담은 리스트 (브로드캐스트용) |
| `GeneratorExit` | 클라이언트가 탭을 닫으면 발생하는 예외 → 정리 작업 |
| `204 No Content` | 요청 성공했지만 응답 본문이 없을 때 쓰는 HTTP 상태코드 |

---

## SSE vs WebSocket 언제 쓸까?

| 상황 | 선택 |
|------|------|
| 실시간 알림, 뉴스피드, 주가 업데이트 | ✅ SSE (서버→클라 단방향이면 충분) |
| 채팅, 게임, 양방향 실시간 통신 | ✅ WebSocket |
| 구현 복잡도 | SSE가 훨씬 간단 (라이브러리 불필요) |

---

## 실행 방법

```bash
pip install flask
python app.py
# http://localhost:5000 접속
```
