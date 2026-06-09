# Anthropic API & MCP 핵심 요약

> **이 폴더에서 배우는 것:**  
> Claude AI를 내 파이썬 코드에서 쓰는 법 → LangChain으로 쉽게 쓰는 법 → MCP로 Claude에게 새 기능 추가하는 법

---

## 전체 구조 한눈에 보기

```
12.ANTHROPIC/
├── 1.basic/          ← Claude API 직접 호출 (기초)
├── 2.langchain/      ← LangChain 라이브러리 활용
├── 3.mcp/            ← MCP 서버/클라이언트 만들기
└── 4.claude_desktop/ ← Claude Desktop에 내 도구 연결하기
```

---

## 1. Basic — Claude API 기초 (`1.basic/`)

### 핵심 개념

```
내 코드 → Anthropic API → Claude → 답변 반환
```

> 비유: Claude에게 편지를 보내고 답장을 받는 것.  
> `client.messages.create()` = 편지 보내기

### 파일별 요약

| 파일 | 배우는 것 | 핵심 포인트 |
|------|-----------|-------------|
| `1.intro.py` | 첫 API 호출 | `client.messages.create()` 기본 사용법 |
| `2.chat.py` | 대화 이어가기 | `messages` 배열에 대화 기록 누적 |
| `3.models.py` | 모델별 비교 | Haiku(빠름) vs Sonnet vs Opus(고성능) |
| `4.thinking.py` | Extended Thinking | AI가 "생각하는 과정"을 보여주는 기능 |

---

### STEP 1 — 첫 API 호출 (`1.intro.py`)

```python
import anthropic
from dotenv import load_dotenv

load_dotenv()                          # .env 파일에서 API 키 읽기
client = anthropic.Anthropic()         # 클라이언트 생성

message = client.messages.create(
    model="claude-haiku-4-5",          # 사용할 모델
    max_tokens=300,                    # 최대 답변 길이
    messages=[{
        "role": "user",
        "content": "안녕! 한 문장으로 너를 소개해줘."
    }]
)

print(message.content[0].text)        # 답변 출력
```

**필수 파라미터 설명:**

| 파라미터 | 설명 | 예시 |
|----------|------|------|
| `model` | 어떤 Claude를 쓸지 | `"claude-haiku-4-5"` |
| `max_tokens` | 답변 최대 글자 수 제한 | `300` |
| `messages` | 대화 내용 (role + content) | `[{"role":"user","content":"..."}]` |

---

### STEP 2 — 대화 이어가기 (`2.chat.py`)

**비유:** 카카오톡 채팅처럼 이전 대화를 기억하게 만들기

```python
messages = []                          # 대화 기록 저장소 (빈 배열)

def ask(question):
    messages.append({'role': 'user', 'content': question})  # 질문 추가

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        messages=messages              # 전체 대화 기록 전달
    )

    answer = response.content[0].text
    messages.append({'role': 'assistant', 'content': answer})  # 답변 추가
    return answer

ask("내 이름은 홍길동이야")
ask("그래서, 내가 누구라고??")          # 이전 대화를 기억함!
```

> **핵심:** `messages` 배열에 대화를 쌓아가면 Claude가 이전 내용을 기억합니다.

---

### STEP 3 — 모델 비교 (`3.models.py`)

```
claude-haiku-4-5   → 가장 빠름, 간단한 작업에 적합
claude-sonnet-4-6  → 균형잡힌 성능, 일반 개발에 추천
claude-opus-4-7/8  → 가장 뛰어난 추론, 복잡한 문제에 사용
```

```python
models = ['claude-haiku-4-5', 'claude-sonnet-4-6', 'claude-opus-4-8']

for model in models:
    start = time.time()
    msg = client.messages.create(model=model, ...)
    elapsed = time.time() - start
    print(f"[{model}] {elapsed:.1f}초, {msg.usage.output_tokens} 토큰")
```

---

### STEP 4 — Extended Thinking (`4.thinking.py`)

**비유:** Claude가 답을 내기 전에 "어떻게 풀지 생각하는 과정"을 보여줌

```python
with client.messages.stream(
    model='claude-opus-4-8',
    max_tokens=2000,
    thinking={"type": "adaptive", "display": "summarized"},  # 생각 활성화
    messages=[{"role": "user", "content": "12 x 13 단계별로 설명해줘"}]
) as stream:
    for event in stream:
        if event.delta.type == "thinking_delta":
            print("[생각]", event.delta.thinking)    # 추론 과정
        elif event.delta.type == "text_delta":
            print("[답변]", event.delta.text)        # 최종 답변
```

---

## 2. LangChain — 더 쉽게 Claude 쓰기 (`2.langchain/`)

### LangChain이란?

> **비유:** Claude를 직접 쓰는 것 vs LangChain으로 쓰는 것  
> = 생 재료로 요리하는 것 vs 밀키트로 요리하는 것  
> LangChain이 복잡한 부분을 미리 처리해 줍니다.

| 파일 | 배우는 것 |
|------|-----------|
| `1.intro.py` | LangChain으로 Claude 1줄 호출 |
| `2.template.py` | 프롬프트 템플릿으로 재사용 가능한 질문 만들기 |

---

### 기본 호출 (`1.intro.py`)

```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model='claude-sonnet-4-6')

response = llm.invoke('인공지능에 대해서 설명해주세요')
print(response.content)
```

> `client.messages.create()` 보다 훨씬 간단하죠?

---

### 프롬프트 템플릿 (`2.template.py`)

**비유:** 빈칸 채우기 문제처럼 질문 틀을 만들어두고 변수만 바꾸는 방법

```python
from langchain_core.prompts import ChatPromptTemplate

# 템플릿 만들기 (변수 = {role}, {concept})
chat_template = ChatPromptTemplate.from_messages([
    ('system', '당신은 {role} 전문가입니다.'),
    ('human', '다음 개념을 설명해주세요: {concept}'),
])

# 체인 연결 (파이프 | 로 연결)
chain = chat_template | llm

# 변수만 채워서 실행
result = chain.invoke({'role': '인공지능', 'concept': '트랜스포머'})
print(result.content)
```

**체인(`|`) 개념:**

```
프롬프트 템플릿 → | → LLM → 결과
(빈칸 채우기)          (Claude)
```

---

## 3. MCP — Claude에게 새 기능 추가하기 (`3.mcp/`)

> **자세한 내용은 `3.mcp/README.md` 참고**

### MCP란?

```
Claude ←→ MCP 서버 ←→ 외부 기능 (계산기, 검색, 파일 등)
```

> 비유: Claude라는 폰에 **앱(기능)을 설치**하는 방법

### 핵심 패턴

```python
# 서버: 도구 만들기
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("내서버")

@mcp.tool()                        # 이 함수를 Claude가 쓸 수 있는 도구로 등록
def add(a: int, b: int) -> int:
    """ 두 수를 더합니다 """        # 설명이 있어야 Claude가 언제 쓸지 알 수 있음
    return a + b

mcp.run()
```

```python
# 클라이언트: 도구 호출하기
await session.initialize()                         # 연결
tools = await session.list_tools()                 # 도구 목록 확인
result = await session.call_tool("add", {"a": 3, "b": 5})  # 도구 실행
```

### 통신 방식 2가지

| 방식 | 언제 쓰나 | 실행 방법 |
|------|-----------|-----------|
| `stdio` | 로컬 테스트 | `mcp.run()` |
| `HTTP` | 네트워크, 여러 클라이언트 | `mcp.run(transport="streamable-http")` |

---

## 4. Claude Desktop 연결 (`4.claude_desktop/`)

> **자세한 내용은 `4.claude_desktop/README.md` 참고**

### 내 MCP 서버를 Claude Desktop 앱에 연결하기

**설정 파일 경로:**
- Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "내서버이름": {
      "command": "python",
      "args": ["/절대경로/내서버.py"]
    }
  }
}
```

재시작 후 채팅창에 🔌 아이콘이 보이면 연결 성공!

---

## 시작하기 (설치 & 실행)

```bash
# 필수 패키지 설치
pip install anthropic python-dotenv

# LangChain 사용 시
pip install langchain-anthropic

# MCP 사용 시
pip install mcp

# .env 파일 만들기 (.env)
ANTHROPIC_API_KEY=sk-ant-xxxxxx

# 실행
python 1.basic/1.intro.py
```

---

## 전체 학습 흐름

```
1. basic/1.intro.py    → Claude API 첫 호출 성공
        ↓
2. basic/2.chat.py     → 대화 이어가기 (멀티턴)
        ↓
3. basic/3.models.py   → 모델별 속도/성능 비교
        ↓
4. basic/4.thinking.py → AI 추론 과정 보기 (Extended Thinking)
        ↓
5. langchain/1.intro.py     → LangChain으로 더 간단하게
        ↓
6. langchain/2.template.py  → 프롬프트 재사용 (템플릿)
        ↓
7. 3.mcp/              → MCP 서버 만들고 도구 추가하기
        ↓
8. 4.claude_desktop/   → Claude Desktop 앱에 내 도구 연결
```

---

## 핵심 용어 사전

| 용어 | 한 줄 설명 |
|------|------------|
| `model` | 어떤 Claude를 쓸지 (haiku=빠름, opus=똑똑함) |
| `max_tokens` | 답변 최대 길이 제한 |
| `messages` | 대화 기록 배열 (role: user/assistant) |
| `temperature` | 답변의 창의성 (0=일정, 1=다양) |
| `stream` | 답변을 한 번에 vs 글자씩 실시간 출력 |
| `Extended Thinking` | AI가 답 내기 전 추론 과정을 보여주는 기능 |
| `LangChain` | AI 앱 개발을 쉽게 만드는 파이썬 라이브러리 |
| `PromptTemplate` | 변수가 있는 재사용 가능한 질문 틀 |
| `Chain (\|)` | 여러 컴포넌트를 연결하는 LangChain 파이프 |
| `MCP` | Claude에게 새 기능(도구)을 추가하는 규격 |
| `@mcp.tool()` | 파이썬 함수를 Claude 도구로 등록하는 장식자 |
| `FastMCP` | MCP 서버를 쉽게 만드는 라이브러리 |
| `stdio` | 로컬 프로세스 간 통신 방식 |
