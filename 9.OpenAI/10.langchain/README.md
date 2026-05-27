# LangChain 핵심 정리

---

## LangChain이 뭔가요?

OpenAI API를 **직접** 쓰면 이렇게 해야 함:

```python
# OpenAI 직접 사용 — 코드가 길고 복잡
import openai
client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "안녕"}]
)
print(response.choices[0].message.content)
```

LangChain을 쓰면 이렇게 줄어듦:

```python
# LangChain 사용 — 짧고 단순
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini")
print(llm.invoke("안녕"))
```

> **결론**: LangChain = OpenAI API를 편하게 쓰게 해주는 포장지

---

## 설치 & 준비

```bash
pip install langchain langchain-openai python-dotenv
```

```
# .env 파일 (API 키는 항상 여기에!)
OPENAI_API_KEY=sk-xxxxxxxx
```

```python
# 코드 맨 위에 항상 이거 먼저
from dotenv import load_dotenv
load_dotenv()
```

---

## 핵심 ① — 가장 기본: invoke()

```python
from langchain_openai import OpenAI

llm = OpenAI(model="gpt-4o-mini")
result = llm.invoke("오늘 저녁은 무엇을 먹을까요?")
print(result)
```

| 코드 | 뜻 |
|------|----|
| `OpenAI(model=...)` | AI 모델 골라서 준비 |
| `llm.invoke("질문")` | AI에게 질문 던지기 |
| `result` | AI의 답변 (문자열) |

---

## 핵심 ② — 두 가지 모델의 차이

LangChain에서 쓰는 모델은 **두 종류**:

```python
from langchain_openai import OpenAI      # 단발성
from langchain_openai import ChatOpenAI  # 대화형
```

### `OpenAI` — 단순 작업용

```python
llm = OpenAI(model='gpt-3.5-turbo-instruct')
print(llm.invoke("다음 문장을 한국말로 번역해줘: Good Morning"))
# → "좋은 아침입니다"
```

- 번역, 요약, 단순 변환처럼 **딱 한 번** 처리하는 작업
- 반드시 `instruct` 모델 사용 (`gpt-3.5-turbo-instruct`)

### `ChatOpenAI` — 대화 / 창작용

```python
llm2 = ChatOpenAI(model='gpt-4o-mini')
print(llm2.invoke("게임 회사 이름 3개 지어줘"))
# → "1. 픽셀스톰 2. 네온게임즈 3. 드래곤워크스"
```

- 아이디어 제안, Q&A, 코딩 도움처럼 **대화가 필요한** 작업
- `gpt-4o-mini`, `gpt-4o` 같은 Chat 모델 사용

---

## 핵심 ③ — 메시지 3종류

AI와 대화할 때 **역할을 나눠서** 전달할 수 있음.

```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

prompt = [
    SystemMessage(content="당신은 창의력이 높은 작명가입니다."),
    HumanMessage(content="게임 회사 이름 3개 지어줘")
]

llm = ChatOpenAI(model='gpt-4o-mini')
print(llm.invoke(prompt))
```

| 메시지 | 역할 | 언제 쓰나 |
|--------|------|-----------|
| `SystemMessage` | AI의 **역할/성격** 설정 | "넌 번역가야", "넌 요리사야" |
| `HumanMessage` | **내가** 하는 말 | 실제 질문 |
| `AIMessage` | **AI가** 이전에 한 말 | 대화 이어갈 때 히스토리로 사용 |

### SystemMessage가 왜 중요한가?

```python
# SystemMessage 없을 때
llm.invoke("사과를 설명해줘")
# → 일반적인 설명

# SystemMessage 있을 때
[
    SystemMessage(content="당신은 5살 아이에게 설명하는 선생님입니다."),
    HumanMessage(content="사과를 설명해줘")
]
# → "사과는 빨간색 과일이에요! 달콤하고 맛있어요~"
```

> SystemMessage로 AI의 **말투, 전문성, 역할**을 완전히 바꿀 수 있음

---

## 주의 — import 경로가 바뀌었음

```python
# ❌ 구버전 (에러 남)
from langchain.llms import OpenAI

# ✅ 신버전 (이걸 써야 함)
from langchain_openai import OpenAI
from langchain_openai import ChatOpenAI
```

---

## 한눈에 보는 전체 구조

```
[내 코드]
    ↓
① 모델 선택
   단순작업  →  OpenAI(model='gpt-3.5-turbo-instruct')
   대화/창작  →  ChatOpenAI(model='gpt-4o-mini')
    ↓
② 질문 준비
   단순 문자열  →  "질문 내용"
   역할 구분    →  [SystemMessage, HumanMessage]
    ↓
③ 실행
   llm.invoke(질문)
    ↓
④ 결과 출력
   print(result)
```

---

## 정리 한 줄 요약

| 개념 | 한 줄 요약 |
|------|-----------|
| LangChain | OpenAI를 쉽게 쓰게 해주는 라이브러리 |
| `OpenAI` | 단발성 작업 (번역, 변환) |
| `ChatOpenAI` | 대화형 작업 (Q&A, 창작) |
| `invoke()` | AI에게 질문 실행 |
| `SystemMessage` | AI 역할 설정 |
| `HumanMessage` | 내 질문 |
| `AIMessage` | AI 이전 답변 (대화 히스토리) |
