# 챗봇 UI + SQLite 대화 저장 실습

> **목표**: 사용자별로 대화 내용을 SQLite DB에 저장하고, 세션(대화방)으로 관리하는 챗봇 만들기

---

## 전체 구조 한눈에 보기

```
브라우저 (사용자)
    ↕  HTTP 요청/응답
Flask 서버 (app.py)
    ↕  SQL 쿼리
SQLite DB (chatgpt.db)
    +
OpenAI API (GPT-4o-mini)
```

**비유**: 카카오톡처럼 생각하면 돼요!
- 브라우저 = 카톡 앱 화면
- Flask 서버 = 카톡 서버
- SQLite DB = 대화 저장 창고
- OpenAI = 대화 상대 AI

---

## 파일 구조

```
5.chatbot_uisqlite_homework/
├── app.py              ← 서버 (Flask) + DB 로직
├── chatgpt.db          ← 대화 저장 DB (실행하면 자동 생성)
└── static/
    ├── index.html      ← 웹페이지 뼈대
    ├── style.css       ← 디자인
    └── script.js       ← 버튼 클릭, API 호출 등 동작
```

---

## 핵심 개념 3가지

### 1. userId vs sessionId

| 개념 | 설명 | 비유 |
|------|------|------|
| `userId` | 사용자 이름 (누가?) | 카톡 계정 이름 |
| `sessionId` | 대화방 ID (어느 대화?) | 카톡 채팅방 |

- 같은 userId가 여러 sessionId를 가질 수 있어요
- "새 대화" 버튼을 누르면 → 새로운 sessionId가 생성됨

```
userId: "chorong"
  └── sessionId: "abc-123"  (1번 대화방)
  └── sessionId: "def-456"  (2번 대화방)
  └── sessionId: "ghi-789"  (3번 대화방)
```

### 2. SQLite DB 테이블 구조

```sql
CREATE TABLE history (
    id         INTEGER  -- 자동 번호 (1, 2, 3...)
    session_id TEXT     -- 어느 대화방인지
    user_id    TEXT     -- 누구의 대화인지
    role       TEXT     -- 'user' 또는 'assistant'
    content    TEXT     -- 실제 메시지 내용
    timestamp  DATETIME -- 언제 보냈는지
)
```

실제 저장 예시:
```
id | session_id | user_id  | role      | content
1  | abc-123    | chorong  | user      | 안녕하세요!
2  | abc-123    | chorong  | assistant | 안녕하세요~ 머하노!
3  | abc-123    | chorong  | user      | 오늘 날씨 어때?
4  | abc-123    | chorong  | assistant | 날씨가 참 좋네예~
```

### 3. 대화 히스토리를 GPT에게 넘기는 방법

GPT는 이전 대화를 기억 못해요. 그래서 매번 **최근 10개 메시지**를 함께 보내줘요.

```python
# DB에서 최근 10개 꺼내기 (최신순 → 역순으로 뒤집기)
cursor.execute(
    'SELECT role, content FROM history WHERE session_id = ? ORDER BY id DESC LIMIT 10',
    (session_id,)
)
rows = rows[::-1]  # 오래된 것이 앞에 오도록 뒤집기

# GPT에게 보내는 최종 메시지 구조
[
  {"role": "system",    "content": "당신은 경상도 사투리 챗봇..."},
  {"role": "user",      "content": "안녕하세요!"},      ← 과거 대화
  {"role": "assistant", "content": "안녕하세요~ 머하노!"},
  {"role": "user",      "content": "오늘 날씨 어때?"},  ← 현재 질문 포함
]
```

---

## API 엔드포인트 (서버와 통신하는 창구)

| 메서드 | 경로 | 역할 |
|--------|------|------|
| `POST` | `/api/chat` | 메시지 보내기 + GPT 답변 받기 |
| `GET`  | `/api/sessions` | 내 대화 목록 가져오기 |
| `GET`  | `/api/history` | 특정 대화방 내용 불러오기 |
| `DELETE` | `/api/history` | 특정 대화방 삭제 |

---

## 대화 흐름 단계별 설명

### 메시지 보내기 전체 흐름

```
① 사용자가 "안녕" 입력 후 전송
       ↓
② script.js → POST /api/chat 요청
   { chatMessage: "안녕", sessionId: "abc-123", userId: "chorong" }
       ↓
③ app.py → DB에 사용자 메시지 저장
   INSERT INTO history (session_id, user_id, role, content)
   VALUES ('abc-123', 'chorong', 'user', '안녕')
       ↓
④ app.py → DB에서 최근 10개 대화 꺼냄
   SELECT role, content FROM history WHERE session_id = 'abc-123' ...
       ↓
⑤ app.py → OpenAI에 전체 대화 + 새 메시지 전송
       ↓
⑥ GPT → "안녕하이소~ 오늘 뭐 도와드릴까예?" 응답
       ↓
⑦ app.py → DB에 GPT 응답 저장
   INSERT INTO history ... VALUES (..., 'assistant', 'GPT 응답 내용')
       ↓
⑧ 브라우저에 응답 전달 → 화면에 말풍선 표시
```

---

## 주요 코드 설명

### `app.py` - DB 초기화

```python
conn = sqlite3.connect('chatgpt.db', check_same_thread=False)
conn.row_factory = sqlite3.Row  # row['컬럼명']으로 접근 가능하게 설정

def init_db():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (...)
    """)
    conn.commit()  # 변경사항 저장 (필수!)

init_db()  # 서버 시작 시 테이블 없으면 자동 생성
```

> `check_same_thread=False` : Flask는 요청마다 쓰레드를 쓰는데,
> SQLite 연결을 여러 쓰레드에서 공유하겠다는 설정이에요.

### `app.py` - 세션 목록 가져오기

```python
@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    # 각 세션의 "첫 번째 사용자 메시지"를 제목으로 사용
    cursor.execute('''
        SELECT session_id, content as title, timestamp
        FROM history
        WHERE user_id = ? AND role = 'user' AND id IN (
            SELECT MIN(id) FROM history WHERE user_id = ? AND role = 'user'
            GROUP BY session_id
        )
        ORDER BY timestamp DESC
    ''', (user_id, user_id))
```

> 카톡 대화목록에서 마지막 메시지가 미리보기로 보이는 것처럼,
> 여기서는 **첫 번째 메시지 앞 30글자**를 제목으로 사용해요.

### `script.js` - sessionId 생성

```javascript
let sessionId = crypto.randomUUID();
// 예: "550e8400-e29b-41d4-a716-446655440000"

// "새 대화" 버튼 클릭 시 → 새 sessionId 생성
newChatBtn.addEventListener('click', () => {
    sessionId = crypto.randomUUID();  // 새 대화방 ID
    resultDiv.innerHTML = '';          // 화면 초기화
});
```

---

## 실행 방법

```bash
# 1. 패키지 설치 (처음 한 번만)
pip install flask openai python-dotenv

# 2. .env 파일 만들기
echo "OPENAI_API_KEY=sk-proj-..." > .env

# 3. 서버 실행
python app.py

# 4. 브라우저에서 열기
# http://127.0.0.1:5000
```

---

## 이전 실습과의 차이점

| 항목 | 이전 (리스트 사용) | 이번 (SQLite 사용) |
|------|-------------------|-------------------|
| 저장 방식 | `history = []` 메모리 | DB 파일에 영구 저장 |
| 서버 재시작 | 대화 사라짐 | 대화 유지됨 |
| 다중 사용자 | 불가 | userId로 구분 가능 |
| 다중 대화방 | 불가 | sessionId로 구분 가능 |
| 대화 삭제 | 불가 | DELETE SQL로 가능 |

---

## 자주 하는 실수

```python
# ❌ commit() 빠뜨리면 DB에 저장 안 됨!
cursor.execute('INSERT INTO history ...')
# conn.commit()  ← 이걸 빠뜨리면 저장 안 됨

# ✅ 항상 commit() 호출
cursor.execute('INSERT INTO history ...')
conn.commit()  # 이게 있어야 실제로 저장됨
```

```python
# ❌ rows[::-1] 빠뜨리면 대화 순서 반대로 GPT에게 전달됨
rows = cursor.fetchall()
# rows = rows[::-1]  ← 이게 없으면 최신 → 오래된 순서로 전달됨

# ✅ 역순으로 뒤집어서 시간순으로 정렬
rows = rows[::-1]  # 오래된 대화가 앞, 최신이 뒤
```
