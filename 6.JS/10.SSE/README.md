# SSE (Server-Sent Events) 핵심 정리

## 1. SSE가 뭔가요?

> **서버가 클라이언트에게 데이터를 알아서 밀어주는 방식**

보통 웹은 이렇게 동작해요:
```
클라이언트: "데이터 줘!" → 서버: "여기!" (끝)
```

SSE는 이렇게 달라요:
```
클라이언트: "구독할게!" → 서버: "알겠어, 새로운 데이터 생기면 계속 보내줄게~"
                                 → (실시간으로 계속 전송)
```

**실생활 비유:**
- 일반 요청 = 편의점 가서 물 한 병 사옴
- SSE = 정수기 구독 → 알아서 물이 계속 옴

---

## 2. yield - SSE의 핵심 개념

SSE를 이해하려면 먼저 **yield**를 알아야 해요.

### yield vs return 차이

```python
# return: 한 번 주고 함수 끝
def test():
    return 1   # 1 주고 종료
    return 2   # ← 절대 실행 안 됨!
```

```python
# yield: 잠깐 멈추고, 다음 호출 때 이어서 실행
def test():
    yield 1   # 1 주고 잠깐 멈춤 (함수 종료 X)
    yield 2   # 다음 호출 시 여기서 이어서 실행
    yield 3
```

**비유:** yield는 "세이브 포인트"가 있는 게임 같아요.
- return = 게임 끄면 처음부터 다시
- yield = 세이브 포인트에서 이어서 재개

---

## 3. Generator (제너레이터)

`yield`가 있는 함수를 호출하면 **Generator** 객체가 만들어져요.

```python
def test():
    print("A")
    yield 1    # 여기서 멈춤

    print("B")
    yield 2    # 여기서 멈춤

    print("C")
    yield 3

x = test()         # Generator 객체 생성 (아직 실행 안 됨!)

print(next(x))     # A 출력 → 1 반환
print(next(x))     # B 출력 → 2 반환
print(next(x))     # C 출력 → 3 반환
```

### 반복문으로 사용하기

```python
x = test()
try:
    while True:
        print(next(x))
except StopIteration:      # 더 이상 yield가 없으면 StopIteration 발생
    print("모든 데이터 사용 완료")
```

---

## 4. yield의 실용적 장점 - 메모리 절약

```python
# 나쁜 방법: 100만 개를 메모리에 다 올림
def numbers_bad():
    return list(range(1000000))  # 메모리 폭발!

# 좋은 방법: 하나씩 그때그때 생성
def numbers():
    for i in range(1000000):
        yield i                  # 메모리 효율적!

for num in numbers():
    print(num)
    if num >= 100:
        break                    # 100까지만 쓰고 중단
```

**비유:** 책 한 권을 통째로 외우는 것 vs 필요한 페이지만 펼쳐보는 것

---

## 5. Flask SSE 실습

### 전체 구조

```
브라우저                    Flask 서버
  │                           │
  │──── GET /stream ─────────▶│  (SSE 연결 시작)
  │◀─── 실시간 메시지 전송 ───│  (서버가 계속 push)
  │                           │
  │──── POST /send ──────────▶│  (메시지 보내기)
  │◀─── 204 No Content ───────│
```

### 서버 코드 (app.py)

```python
from flask import Flask, Response
from queue import Queue

clients = []   # 연결된 사용자들을 담는 리스트

@app.route("/stream")
def stream():
    def event_stream():
        q = Queue()
        clients.append(q)          # 새 사용자 등록
        try:
            yield "data: 연결됨!\n\n"  # 웹표준 SSE 형식: data: 메시지\n\n

            while True:
                message = q.get()  # 큐에 메시지 올 때까지 대기
                yield f"data: {message}\n\n"

        finally:
            clients.remove(q)      # 연결 끊기면 목록에서 제거

    return Response(event_stream(), mimetype="text/event-stream")
```

**핵심:** `yield`로 연결을 끊지 않고 계속 데이터를 흘려보냄!

### 클라이언트 코드 (index.html)

```javascript
// SSE 연결 시작
const source = new EventSource("/stream");

source.onopen = () => {
    console.log("서버와 연결됨");
}

// 서버에서 메시지 오면 자동으로 실행
source.onmessage = (event) => {
    console.log("받은 메시지:", event.data);
}
```

---

## 6. SSE 데이터 형식 (웹 표준)

SSE는 특정 형식으로 데이터를 전송해야 해요:

```
data: 여기에 메시지 내용\n\n
```

- 반드시 `data:` 로 시작
- 반드시 `\n\n` (빈 줄 두 개)로 끝
- `mimetype="text/event-stream"` 헤더 필수

---

## 7. SSE vs WebSocket 비교

| 구분 | SSE | WebSocket |
|------|-----|-----------|
| 방향 | 서버 → 클라이언트 (단방향) | 양방향 |
| 프로토콜 | 일반 HTTP | ws:// |
| 사용 예 | 뉴스피드, 알림, AI 스트리밍 | 채팅, 게임 |
| 구현 난이도 | 쉬움 | 보통 |
| 자동 재연결 | 브라우저가 자동으로 함 | 직접 구현 필요 |

---

## 8. 학습 흐름 요약

```
1.yield.py   →  yield 기본 개념 (return과의 차이)
2.yield.py   →  yield와 중간 작업들 + StopIteration 처리
3.yield.py   →  yield의 메모리 절약 활용
1.flask_sse/ →  yield를 실제 SSE에 적용 (서버 + 브라우저)
```

> **핵심 한 줄 요약:**
> `yield`로 함수를 멈췄다 이어주는 Generator → 이걸 HTTP에 적용하면 SSE!
