# LangChain Memory (대화 기억) 핵심 요약

> AI 챗봇이 이전 대화를 기억하게 만드는 방법을 배웁니다.

---

## AI는 왜 기억을 못할까? (`1.review.py`)

기본 LLM은 **매 질문을 독립적으로 처리**합니다.  
마치 매번 새로운 사람에게 말하는 것처럼요.

```
나: "저는 홍길동입니다."
AI: "안녕하세요!"

나: "제 이름이 뭐라고 했죠?"
AI: "죄송해요, 모르겠어요." ← 기억 못함!
```

### 해결책: `MessagesPlaceholder`로 대화 공간 만들기

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 챗봇입니다."),
    MessagesPlaceholder("history"),  # ← 여기에 이전 대화를 삽입!
    ("user", "{input}")
])
```

`MessagesPlaceholder`는 프롬프트 안에 **이전 대화를 끼워 넣을 공간**을 만들어 줍니다.

---

## 대화 저장 방법 3가지

| 방법 | 저장 위치 | 프로그램 종료 후 | 사용 상황 |
|------|-----------|----------------|-----------|
| **InMemory** | RAM (메모리) | ❌ 사라짐 | 테스트, 개발 |
| **File** | JSON 파일 | ✅ 유지 | 간단한 저장 |
| **SQLite** | DB 파일 | ✅ 유지 | 실제 서비스 |

---

## 1단계: 메모리에 저장 (`2.inmemory.py`)

> 비유: **포스트잇** — 빠르지만 컴퓨터 끄면 사라짐

```python
from langchain_core.chat_history import InMemoryChatMessageHistory

history = InMemoryChatMessageHistory()  # 대화 저장소 생성

def chat(message):
    answer = chain.invoke({
        "input": message,
        "history": history.messages[-10:],  # 최근 10개만 전달 (토큰 절약!)
    })
    history.add_user_message(message)  # 내 질문 저장
    history.add_ai_message(answer)     # AI 답변 저장
```

### 핵심 포인트
- `history.messages[-10:]` → **최근 10개 대화만** 사용 (비용 절감)
- 프로그램 종료 시 대화 내용이 **사라짐**

---

## 2단계: 파일에 저장 (`3.infile.py`)

> 비유: **일기장** — 노트북을 닫아도 내용이 남아있음

```python
from langchain_community.chat_message_histories import FileChatMessageHistory

history = FileChatMessageHistory("history.json")  # JSON 파일에 저장
```

나머지 코드는 InMemory와 **완전히 동일**합니다.  
저장소만 바꾸면 끝!

```json
// history.json 파일이 자동 생성됨
[
  {"type": "human", "data": {"content": "제 이름은 곽길동입니다."}},
  {"type": "ai",    "data": {"content": "네, 곽길동님 반갑습니다."}}
]
```

---

## 파일 내용 읽기 (`4.utf_fileread.py`)

저장된 `history.json`을 보기 좋게 출력하는 유틸리티입니다.

```
=== 4 메시지 ===
01. [사용자  ] 제 이름은 곽길동 입니다.
02. [챗봇    ] 네, 곽길동님 반갑습니다.
03. [사용자  ] 저는 서핑을 좋아합니다.
04. [챗봇    ] 멋진 취미네요!
```

---

## 3단계: 데이터베이스에 저장 (`5.insqlite.py`)

> 비유: **엑셀 파일** — 여러 사용자 데이터를 체계적으로 관리

```python
from langchain_community.chat_message_histories import SQLChatMessageHistory
from sqlalchemy import create_engine

engine = create_engine("sqlite:///chat_history.db")

# session_id로 사용자를 구분!
history = SQLChatMessageHistory(session_id="default", connection=engine)
```

### 파일 vs SQLite 비교

```
파일 방식:   history_user1.json, history_user2.json  (파일 여러 개)
SQLite 방식: chat_history.db 파일 하나 + session_id로 구분  (관리 용이)
```

---

## 4단계: 멀티 유저 세션 관리 (`6.session.py`)

> 비유: **호텔 방** — 투숙객마다 다른 방 번호로 구분

실제 서비스에서는 여러 사용자가 동시에 사용합니다.  
각 사용자의 대화를 **session_id**로 분리해서 관리합니다.

```python
from langchain_core.runnables.history import RunnableWithMessageHistory

# 세션 저장소
sessions: dict[str, InMemoryChatMessageHistory] = {}

def get_session_history(session_id: str):
    if session_id not in sessions:
        sessions[session_id] = InMemoryChatMessageHistory()  # 새 방 만들기
    return sessions[session_id]

# 메모리 기능이 추가된 체인
chain_with_memory = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)
```

### 사용 방법

```python
# session_id만 다르게 하면 완전히 분리된 대화!
chat("제 이름은 홍길동입니다.", session_id="user-A")
chat("제 이름은 김철수입니다.", session_id="user-B")

chat("저는 누구인가요?", session_id="user-A")  # → 홍길동
chat("저는 누구인가요?", session_id="user-B")  # → 김철수
```

---

## 전체 구조 한눈에 보기

```
사용자 입력
    ↓
[프롬프트]
  - system: AI 역할 설정
  - history: 이전 대화 내용 ← 저장소에서 불러옴
  - user: 현재 질문
    ↓
[LLM] gpt-4o-mini
    ↓
AI 답변 출력
    ↓
[저장소] 질문 + 답변 저장
  - InMemory (RAM)
  - File (JSON)
  - SQLite (DB)
```

---

## 핵심 용어 정리

| 용어 | 설명 |
|------|------|
| `MessagesPlaceholder` | 프롬프트에 대화 기록을 삽입할 자리 표시자 |
| `InMemoryChatMessageHistory` | RAM에 대화를 저장하는 클래스 |
| `FileChatMessageHistory` | JSON 파일에 대화를 저장하는 클래스 |
| `SQLChatMessageHistory` | SQLite DB에 대화를 저장하는 클래스 |
| `RunnableWithMessageHistory` | 세션 관리를 자동화해주는 래퍼 |
| `session_id` | 사용자를 구분하는 고유 ID |
| `history.messages[-10:]` | 최근 10개의 메시지만 사용 (토큰 절약) |

---

## 실습 순서 추천

```
1.review.py     → 메모리가 왜 필요한지 이해
2.inmemory.py   → RAM에 저장하는 기본 패턴 익히기
3.infile.py     → 파일로 영구 저장하기
4.utf_fileread.py → 저장된 내용 확인하기
5.insqlite.py   → DB로 저장하기
6.session.py    → 멀티 유저 세션 관리 (심화)
```
