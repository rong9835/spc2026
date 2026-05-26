# 스트리밍 채팅 핵심요약

## 스트리밍이란?

> 일반 응답 vs 스트리밍 응답

```
일반 응답: [생각중...5초...] → "안녕하세요! 저는 AI입니다."  (한 번에 딱)

스트리밍:  "안" → "녕" → "하" → "세" → "요" → ...  (글자가 흘러나옴)
```

마치 **유튜브 로딩**과 같아요.
- 일반 응답 = 영상 전체 다운로드 후 재생
- 스트리밍 = 받으면서 바로 재생

---

## 전체 흐름 한눈에 보기

```
브라우저 (index.html)              서버 (app.py)              OpenAI
      │                                 │                        │
      │  1. 메시지 POST /stream ──────▶│                        │
      │                                 │  2. stream=True ──────▶│
      │                                 │                        │
      │  ◀── data: {"content":"안"}\n\n │  ◀── chunk "안" ───── │
      │  ◀── data: {"content":"녕"}\n\n │  ◀── chunk "녕" ───── │
      │  ◀── data: [DONE]\n\n ──────── │  ◀── 완료 ──────────── │
```

---

## 서버 코드 (app.py) 분석

### 1. 준비 작업
```python
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
app = Flask(__name__, static_folder='public')
```
- OpenAI 연결 준비
- Flask 서버 생성 (`public` 폴더 안의 파일을 웹에 제공)

---

### 2. 스트리밍 응답 핵심 — `generate_response()`

```python
response = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[...],
    stream=True          # ← 이게 핵심! True로 바꾸면 스트리밍 시작
)
```

| 옵션 | 동작 |
|------|------|
| `stream=False` (기본) | 답변 전체를 한 번에 받음 |
| `stream=True` | 답변을 조각조각 나눠서 받음 |

---

### 3. 조각(chunk) 하나씩 꺼내기

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        yield f"data: {json.dumps({'content': content})}\n\n"
yield "data: [DONE]\n\n"
```

- `chunk.choices[0].delta.content` = 이번에 도착한 글자 조각
- `yield` = 조각이 올 때마다 즉시 브라우저로 전송
- `[DONE]` = 다 끝났다는 신호

> **비유**: 수도꼭지에서 물이 한 방울씩 떨어지는 것처럼, 글자가 하나씩 흘러나옴

---

### 4. SSE (Server-Sent Events) 형식

```
data: {"content": "안"}\n\n
data: {"content": "녕"}\n\n
data: [DONE]\n\n
```

- `data: ` 로 시작해야 하는 규칙
- `\n\n` (빈 줄 두 개)으로 끝나야 하는 규칙
- `mimetype="text/event-stream"` 으로 응답해야 브라우저가 SSE로 인식

---

## 프론트엔드 코드 (index.html) 분석

### 1. 스트림 요청 보내기

```javascript
const response = await fetch('/stream', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({message})
});
```
- 일반 fetch 요청과 동일하게 시작

---

### 2. 스트림 읽기 — 일반 응답과 차이점

```javascript
// 일반 응답 (예전 방식)
const data = await response.json();  // 한 번에 다 기다림

// 스트리밍 방식
const reader = response.body.getReader();  // 조금씩 읽는 도구
const decoder = new TextDecoder();          // 바이트 → 문자열 변환기
```

---

### 3. while 루프로 계속 읽기

```javascript
while (true) {
    const { done, value } = await reader.read();  // 조각 하나 읽기
    if (done) break;                               // 다 끝나면 탈출

    const chunk = decoder.decode(value);           // 바이트 → 문자열
    const lines = chunk.split('\n');               // 줄 단위로 쪼개기

    for (const line of lines) {
        if (line.startsWith('data: ')) {           // "data: " 로 시작하면
            const data = line.slice(6);            // "data: " 6글자 제거
            if (data === '[DONE]') continue;       // 완료 신호면 건너뜀
            
            const parsed = JSON.parse(data);       // JSON 파싱
            if (parsed.content) {
                fullText += parsed.content;        // 누적
                chat.innerHTML = fullText;         // 화면 업데이트
            }
        }
    }
}
```

> **비유**: 편의점 택배처럼 박스가 올 때마다 바로 열어보는 것

---

## 핵심 개념 정리

| 개념 | 설명 | 비유 |
|------|------|------|
| `stream=True` | OpenAI가 조각씩 보냄 | 타이핑하듯이 |
| `yield` | 조각 오면 즉시 전송 | 실시간 중계 |
| `text/event-stream` | SSE 형식임을 선언 | 채널 설정 |
| `getReader()` | 스트림 읽는 도구 | 수신기 |
| `TextDecoder` | 바이트를 글자로 변환 | 번역기 |
| `[DONE]` | 전송 완료 신호 | "이상 끝" |

---

## 파일 구조

```
1.content/
├── app.py           # Flask 서버 + OpenAI 스트리밍
└── public/
    └── index.html   # 채팅 UI + 스트림 수신 코드
```

---

## 실행 방법

```bash
pip install flask openai python-dotenv
python app.py
# → http://localhost:5000 접속
```

`.env` 파일 필요:
```
OPENAI_API_KEY=sk-...
```
