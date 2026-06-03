# LangChain Agent (에이전트) 핵심 요약

> **에이전트란?** LLM(AI)에게 "도구(Tool)"를 주어, 스스로 생각하고 도구를 골라 사용하게 만드는 시스템

---

## 핵심 개념 한눈에 보기

```
일반 LLM:  질문 → AI → 답변
에이전트:  질문 → AI가 생각 → 도구 선택 → 도구 실행 → 결과 확인 → 최종 답변
```

AI가 마치 사람처럼 **"어떤 도구를 써야 하지? → 써보자 → 결과 확인 → 답변"** 과정을 스스로 반복합니다.

---

## 폴더 구조

```
8.agent/
├── 1.legacy(deprecated)/   # ❌ 옛날 방식 (참고용, 지금은 안 씀)
├── 2.intro/                # ✅ 기본 에이전트 사용법
├── 3.custom/               # ✅ 나만의 도구 만들기
└── 4.hitl/                 # ✅ 사람이 중간에 개입하는 에이전트 (Human-in-the-Loop)
```

---

## 📁 1.legacy(deprecated) — 옛날 방식 (사용 안 함)

> 참고만 하세요. LangChain이 업데이트되면서 이 방식은 더 이상 권장하지 않습니다.

### `1.intro_wiki_veryold.py`

**옛날 방식**으로 에이전트 만들기 (지금은 `create_agent`를 씁니다)

```python
# ❌ 옛날 방식 (Deprecated)
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,  # 복잡한 설정 필요
    verbose=True
)
```

| 항목 | 내용 |
|------|------|
| 사용 도구 | `initialize_agent`, `AgentType` |
| 상태 | 사용 중단 (Deprecated) |
| 기억할 것 | 지금은 `create_agent()` 함수로 대체됨 |

---

## 📁 2.intro — 기본 에이전트 사용법

> 현대적인 방식으로 에이전트를 만드는 기초를 배웁니다.

### `2.intro_agent.py` — 가장 기본적인 에이전트

**핵심:** `@tool` 데코레이터로 함수를 도구로 만들기

```python
@tool
def calculator(expression):
    """ 수학 식을 계산한다. 예: 53 * 7 + 2 """  # ← AI가 이 설명을 읽고 도구를 선택!
    return str(eval(expression))

agent = create_agent(llm, [calculator])
```

> 💡 **포인트:** 함수 안의 `"""설명"""` (docstring)이 AI가 읽는 사용 설명서입니다.
> 설명을 잘 써야 AI가 적절한 상황에서 도구를 사용합니다.

---

### `3.intro_wiki.py` — 위키피디아 도구 사용

**핵심:** LangChain이 제공하는 기성품 도구 사용하기

```python
tools = load_tools(["wikipedia"])       # 위키피디아 도구 불러오기
agent = create_agent(llm, tools)        # 에이전트 생성
result = agent.invoke({"messages": [("user", "파이썬은 누가 만들었어?")]})
```

> 💡 **포인트:** `load_tools(["도구이름"])` 으로 미리 만들어진 도구를 가져올 수 있습니다.

---

### `4.intro_wiki_new.py` — 한국어/영어 위키 2개 동시 사용

**핵심:** 같은 종류의 도구를 여러 개 만들고, AI가 상황에 맞게 선택하게 하기

```python
wiki_ko = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(lang="ko"),
    name="wiki_ko",
    description="한국어 위키피디어. 한국 사건/인물/개념"  # ← AI가 읽는 설명
)

wiki_en = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(lang="en"),
    name="wiki_en",
    description="English Wikipedia. 글로벌/영어권 주제"  # ← AI가 읽는 설명
)

agent = create_agent(llm, [wiki_en, wiki_ko], system_prompt=system_prompt)
```

> 💡 **포인트:**
> - `name`과 `description`으로 도구를 구분시킵니다
> - AI가 질문 내용에 따라 한국어/영어 위키 중 알아서 선택합니다
> - `system_prompt`로 도구 사용 규칙을 지시할 수 있습니다

---

### `5.intro_websearch.py` — 실시간 웹 검색

**핵심:** Tavily를 이용해 실시간 인터넷 검색하기

```python
from langchain_tavily import TavilySearch

web_search = TavilySearch(max_results=3)    # 결과 3개까지
agent = create_agent(llm, [web_search])

result = agent.invoke({"messages": [("user", "LangChain 의 최신 버전은??")]})
```

> 💡 **포인트:**
> - 일반 LLM은 학습 날짜 이후 정보를 모릅니다
> - 웹 검색 도구를 주면 **실시간 최신 정보**를 답변에 활용할 수 있습니다
> - Tavily 외에도 Google, Serper 등 다양한 검색 도구가 있습니다

---

### `6.intro_calc.py` — 수학 계산 도구

**핵심:** `llm-math` 기성품 수학 도구 사용하기

```python
tools = load_tools(["llm-math"], llm=llm)   # 수학 계산 도구
agent = create_agent(llm, tools)

result = agent.invoke({"messages": [("user", "(12.5 * 4) + 7 의 제곱근을 계산하시오.")]})
```

> 💡 **포인트:** AI는 복잡한 수학을 혼자 하면 틀립니다. `llm-math` 도구는 정확한 수식 계산을 도와줍니다.

---

### `7.show_tools.py` — 사용 가능한 모든 도구 목록 보기

**핵심:** LangChain에서 제공하는 기성품 도구 전체 목록 확인

```python
from langchain_community.agent_toolkits.load_tools import get_all_tool_names

names = sorted(get_all_tool_names())
for name in names:
    print(f" - {name}")
```

> 💡 **포인트:** 어떤 도구가 있는지 목록을 보고, 필요한 것을 `load_tools(["도구이름"])`으로 가져다 쓰세요.

---

## 📁 3.custom — 나만의 도구 만들기

> 기성품 도구로 해결이 안 될 때, 직접 도구를 만드는 방법을 배웁니다.

### `1.mytool.py` — 안전한 계산기 도구

**핵심:** `eval()` 함수의 보안 취약점을 막는 방법

```python
@tool
def calculator(expression: str) -> str:
    """수학 식을 계산한다. 예: 53 * 7 + 2"""
    try:
        # ✅ 안전한 eval: 내장 함수 사용 금지
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"계산 오류: {e}"
```

> ⚠️ **중요 보안 포인트:**
> - `eval(expression)` 만 쓰면 AI가 `__import__('os').system(...)` 같은 위험한 코드를 실행시킬 수 있습니다
> - `{"__builtins__": {}}` 를 추가하면 시스템 명령 실행을 차단합니다
> - 도구는 AI가 자동으로 호출하므로 **항상 예외처리**를 해야 합니다

---

### `2.mytools.py` — 여러 도구를 동시에 사용하기

**핵심:** 도구 여러 개를 만들고 AI가 상황에 맞게 자동 선택하게 하기

```python
@tool
def get_word_length(word: str) -> int:
    """ 단어의 글자 수를 세어서 숫자로 반환한다 """
    return len(word)

@tool
def calculate_tip(amount: float, percent: float) -> float:
    """ 음식점 영수증 금액과 팁 비율(%)을 입력받아서 팁 금액을 계산한다 """
    return amount * percent / 100

@tool
def search_user(user_id: str) -> dict:
    """ 사용자 ID로 사용자 정보를 조회한다 """
    db = {"u001": {"name": "홍길동", "city": "서울"}}
    return db.get(user_id, {})

# 도구 목록을 LLM에 연결
llm_with_tools = llm.bind_tools(tools)
```

> 💡 **핵심 흐름:**
> ```
> 질문 → AI가 어떤 도구를 쓸지 결정 → tool_calls 에 담아서 반환
>      → 우리가 직접 tool.invoke(args) 로 실행 → 결과 출력
> ```
> `bind_tools()`는 "이런 도구들이 있어" 라고 AI에게 알려주는 것이고,
> 실제 실행은 `name2tool[call['name']].invoke(call['args'])` 로 합니다.

---

### `3.pydantic.py` — Pydantic으로 도구 입력값 검증하기

**핵심:** 도구 입력값의 형식과 제약조건을 명확하게 지정하기

```python
from pydantic import BaseModel, Field

class SendEmailInput(BaseModel):
    to: str = Field(description="수신자 이메일 주소 (반드시 유효한 이메일 형식)")
    subject: str = Field(description="이메일 제목 (50자 이내)")
    body: str = Field(description="이메일 본문 (반드시 한국어로 작성)")
    priority: Literal["low", "normal", "high"] = Field(default="normal")

@tool(args_schema=SendEmailInput)   # ← Pydantic 스키마 연결
def send_email(to, subject, body, priority="normal") -> str:
    """ 사용자가 요청할 때 이메일을 보낸다. """
    ...
```

> 💡 **왜 Pydantic을 쓰나요?**
> - AI가 도구를 호출할 때 잘못된 값을 넣을 수 있습니다
> - Pydantic을 쓰면 **타입, 범위, 형식**을 자동으로 검증합니다
> - `description`에 설명을 쓰면 AI가 올바른 값을 넣도록 유도합니다
>
> **도구를 못 찾으면?** 시스템 프롬프트로 행동 방침을 지시할 수 있습니다:
> ```python
> SYSTEM = "적합한 도구가 없으면 '해당 작업을 수행할 수 있는 도구가 없습니다.'라고 답변하라"
> ```

---

### `4.sqltool.py` — SQL 데이터베이스 조회 도구

**핵심:** AI가 자연어 질문을 SQL로 변환해서 데이터베이스를 조회하게 하기

```python
@tool
def run_sql(query: str) -> str:
    """ SQLite DB에 SQL 구문을 실행하고 결과를 반환한다. """
    cur = conn.execute(query.strip().rstrip(";"))
    rows = cur.fetchall()
    ...

SYSTEM = f"""
당신은 SQLite 데이터 분석가입니다. 아래 스키마를 사용해서 질문에 응답하시오.
[스키마]
{SCHEMA}
"""

agent = create_agent(llm, [run_sql], system_prompt=SYSTEM)

# 자연어 질문 → AI가 SQL로 변환 → 실행 → 답변
agent.invoke({"messages": [("user", "서울 사는 사용자는 몇 명이야?")]})
# AI가 자동으로: SELECT COUNT(*) FROM users WHERE city='서울' 실행
```

> 💡 **핵심 패턴:**
> 1. 데이터베이스 스키마(테이블 구조)를 시스템 프롬프트에 알려준다
> 2. AI가 질문을 보고 적절한 SQL을 작성해 `run_sql` 도구를 호출한다
> 3. 결과를 받아서 자연어로 답변한다

---

## 📁 4.hitl — 사람이 중간에 개입하는 에이전트

> **HITL (Human-in-the-Loop):** 에이전트가 도구를 실행하기 **직전에 멈추고**, 사람이 확인·수정·취소할 수 있게 하는 패턴
> 송금, 삭제, 이메일 전송처럼 **되돌리기 어려운 작업**에 꼭 필요합니다.

```
일반 에이전트:  질문 → AI 결정 → 도구 자동 실행 → 답변
HITL 에이전트:  질문 → AI 결정 → ⏸️ 잠깐 멈춤 → 사람 확인 → 도구 실행 → 답변
```

### 핵심 코드 패턴

```python
from langgraph.checkpoint.memory import MemorySaver

checkpoint = MemorySaver()  # 멈춘 상태를 저장하는 체크포인트

# interrupt_before=["tools"] : 도구 실행 직전에 항상 멈춤
agent = create_agent(llm, [send_payment], checkpointer=checkpoint, interrupt_before=["tools"])

config = {"configurable": {"thread_id": "t001"}}  # 대화 세션 구분용 ID
```

---

### `1.ask.py` — 기본 확인 패턴

**핵심:** 도구 실행 전 사람에게 y/n 확인 받기

```python
# 1단계: 에이전트 실행 → 도구 직전에 자동 멈춤
result = agent.invoke({"messages": [("user", question)]}, config=config)
call = result["messages"][-1].tool_calls[0]   # AI가 어떤 도구를 부르려는지 확인
print(f"[일시정지] {call['name']} ({call['args']})")

# 2단계: 사람이 확인
if input("이대로 실행할까요? (y/n)").strip().lower() == 'y':
    result = agent.invoke(None, config=config)  # None = "멈춘 곳에서 이어서 실행"
```

> 💡 **핵심 개념:**
> - `interrupt_before=["tools"]` → 도구 실행 직전에 멈추도록 설정
> - `agent.invoke(None, config)` → 저장된 상태에서 이어서 실행

---

### `2.ask2.py` — 중요한 도구만 확인 (스마트 HITL)

**핵심:** 모든 도구가 아니라 **위험한 도구(송금)만** 사람 확인, 나머지는 자동 실행

```python
while result["messages"][-1].tool_calls:
    last_msg = result["messages"][-1]

    if last_msg.tool_calls[0]['name'] != 'send_payment':
        # 잔액 조회처럼 안전한 도구 → 자동 실행
        result = agent.invoke(None, config=config)
        continue

    # 송금처럼 위험한 도구 → 사람 확인 요청
    if input("이대로 실행할까요? (y/n) ").strip().lower() == 'y':
        result = agent.invoke(None, config=config)
```

> 💡 **포인트:**
> - 모든 동작을 멈추면 불편합니다. 중요한 것만 확인하세요
> - 도구 이름(`call['name']`)으로 중요도를 구분합니다

---

### `3.ask_edit.py` — 상태를 직접 수정하기

**핵심:** AI가 제안한 값을 사람이 **직접 수정**한 후 실행하기

```python
# 1. 멈춰있는 AI 메시지 조회
ai_msg = agent.get_state(config).values["messages"][-1]
call = ai_msg.tool_calls[0]   # AI가 하려던 도구 호출

# 2. 값을 수정 (10000원 → 5000원으로)
edited = {**call, "args": {**call['args'], 'amount': 5000}}
fixed = AIMessage(content=ai_msg.content, tool_calls=[edited], id=ai_msg.id)

# 3. 수정된 상태를 에이전트에 덮어쓰기
agent.update_state(config, {"messages": [fixed]})

# 4. 수정된 값으로 이어서 실행
result = agent.invoke(None, config=config)
```

> 💡 **포인트:**
> - `agent.get_state(config)` → 현재 멈춰있는 상태 조회
> - `agent.update_state(config, ...)` → 상태를 사람이 원하는 값으로 교체
> - 이 패턴으로 AI의 실수를 실행 전에 수정할 수 있습니다

---

### `4.ask_edit2.py` — 완전한 HITL (확인/취소/수정)

**핵심:** 실무에서 쓸 수 있는 완성형 HITL — 세 가지 선택지 제공

```python
print(f"\n{args['recipient']} 에게 송금을 진행하시겠습니까?")
print("  1. 예(송금)")
print("  2. 아니오(취소)")
print("  3. 금액 수정")
choice = input("선택 (1/2/3): ").strip()

if choice == "2":
    print("[취소]")
elif choice == "3":
    new_amount = int(input("새 송금 금액(원): "))
    # update_state로 금액 수정 후 실행
    ...
else:
    result = agent.invoke(None, config=config)  # 그대로 실행
```

> 💡 **실무 포인트:**
> - 1번(실행) / 2번(취소) / 3번(수정) 세 갈래로 처리
> - 금융, 이메일, 삭제 작업 등 **취소 불가능한 작업**에 반드시 적용하세요

---

## 전체 학습 흐름 요약

```
1️⃣  옛날 방식 (initialize_agent)
        ↓ 업그레이드
2️⃣  새로운 방식 (create_agent + @tool)
        ↓ 기성품 도구 활용
3️⃣  load_tools(): 위키, 수학, 웹검색 도구
        ↓ 커스터마이징
4️⃣  나만의 도구: @tool 데코레이터로 직접 제작
        ↓ 고급화
5️⃣  Pydantic 검증 + SQL 도구 = 실무형 에이전트
        ↓ 안전성 강화
6️⃣  HITL: 도구 실행 전 사람이 확인·수정·취소 = 실무 안전 에이전트
```

---

## 자주 쓰는 코드 패턴

### 기본 에이전트 만들기
```python
from langchain.agents import create_agent
from langchain_core.tools import tool

@tool
def my_tool(input: str) -> str:
    """ 도구 설명 (AI가 이 설명을 읽고 도구 사용 여부를 결정) """
    return "결과"

agent = create_agent(llm, [my_tool])
result = agent.invoke({"messages": [("user", "질문")]})
print(result["messages"][-1].content)  # 마지막 메시지 = 최종 답변
```

### 메시지 흐름 출력하기
```python
for m in result["messages"]:
    if hasattr(m, "tool_calls") and m.tool_calls:
        for c in m.tool_calls:
            print(f"[도구 호출] {c['name']}({c['args']})")  # AI가 어떤 도구를 썼는지
    if m.type == "tool":
        print(f"[도구 결과] {m.content}")                   # 도구 실행 결과
```

---

## 필요한 패키지 설치

```bash
pip install langchain langchain-openai langchain-community
pip install wikipedia          # 위키피디아 도구
pip install langchain-tavily   # 웹 검색 도구
pip install numexpr            # 수학 계산 도구 (llm-math)
pip install pydantic           # 입력값 검증
pip install langgraph          # HITL (Human-in-the-Loop) 체크포인트
```
