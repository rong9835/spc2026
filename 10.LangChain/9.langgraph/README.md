# LangGraph 핵심 요약

> LangGraph = LangChain 위에서 **AI가 여러 단계를 거쳐 생각하는 흐름**을 만드는 도구

---

## 핵심 개념 (3가지만 기억하기)

| 개념 | 쉬운 비유 | 설명 |
|------|-----------|------|
| **노드 (Node)** | 공장의 작업대 | 실제 일을 처리하는 함수 |
| **엣지 (Edge)** | 컨베이어 벨트 | 노드 사이의 이동 경로 |
| **상태 (State)** | 메모장 | 작업 중에 기억하고 공유하는 데이터 |

```
START → [노드1] → [노드2] → END
         ↑엣지↑    ↑엣지↑
```

---

## 1. 기본 구조 (`1.intro.py`)

**뭘 하나요?** 가장 단순한 AI 챗봇 — 질문 → 응답 1번

```
START ──▶ model ──▶ END
```

### 핵심 코드 패턴

```python
# 1. 그래프 생성 (MessagesState = 기본 메시지 저장소)
graph = StateGraph(state_schema=MessagesState)

# 2. 노드 추가 (실제 작업 함수 등록)
graph.add_node("model", call_model)

# 3. 엣지 연결 (흐름 지정)
graph.add_edge(START, "model")
graph.add_edge("model", END)

# 4. 컴파일 (완성!)
app = graph.compile()

# 5. 실행
result = app.invoke({"messages": [HumanMessage(content="안녕!")]})
```

### 포인트
- `MessagesState` : LangGraph가 기본 제공하는 메시지 목록 상태
- `call_model` 함수가 `{"messages": response}` 를 반환하면 상태에 자동으로 추가됨

---

## 2. 메모리 (대화 기억) (`2.memory.py`)

**뭘 하나요?** AI가 이전 대화를 기억하는 챗봇

```
START ──▶ model ──▶ END
              ↑
           💾 메모리
```

### 핵심 코드 패턴

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()

# 컴파일 시 checkpointer 연결 (이게 핵심!)
app = graph.compile(checkpointer=memory)

# thread_id = "대화방 ID" (같은 ID면 같은 대화로 인식)
config = {"configurable": {"thread_id": "방1"}}

app.invoke({"messages": [HumanMessage("내 이름은 김철수야")]}, config=config)
app.invoke({"messages": [HumanMessage("내 이름이 뭐야?")]}, config=config)
# → "당신의 이름은 김철수입니다!" (기억함!)
```

### 포인트
- `MemorySaver` : 메모리(RAM)에 대화 내용을 저장
- `thread_id` : 대화방을 구분하는 ID. **다른 ID = 다른 사람, 기억 공유 안 됨**

### 실험 결과 (코드에서)
```
thread1: "내 이름은 김철수"  →  "내 직업은 프로그래머"  →  이름+직업 기억 ✅
thread2: "내 이름은 홍길동"  →  thread1과 독립적으로 기억됨 ✅
```

---

## 3. 분기 처리 (조건부 라우팅) (`3.branch.py`)

**뭘 하나요?** 사용자 질문에 따라 다른 전문가에게 연결

```
                      ┌─────────┐
                ┌──▶ │ weather │ ──▶ END
START ──▶ router│──▶ │  news   │ ──▶ END
                └──▶ │  chat   │ ──▶ END
                      └─────────┘
```

### 핵심 코드 패턴

```python
# 라우터 함수: 어디로 보낼지 결정 (문자열 반환)
def topic_router(state, config) -> str:
    last_message = state["messages"][-1].content
    if "날씨" in last_message:
        return "weather"
    if "뉴스" in last_message:
        return "news"
    return "chat"

# 조건부 엣지 등록 (일반 엣지와 다름!)
graph.add_conditional_edges(
    "router",         # 출발 노드
    topic_router,     # 어디로 갈지 결정하는 함수
    path_map={        # 반환값 → 노드 이름 매핑
        "weather": "weather",
        "news": "news",
        "chat": "chat"
    }
)
```

### 포인트
- `add_edge` : 항상 같은 곳으로 이동
- `add_conditional_edges` : 조건에 따라 다른 곳으로 이동
- 각 전문가 노드는 독립적으로 작동 → 역할 분리 가능

---

## 전체 흐름 한 눈에 보기

```
1.intro.py   →  단순 질문-응답
2.memory.py  →  대화 기억 추가
3.branch.py  →  주제별 전문가 분기
```

### 공통 구조 (항상 같음)

```python
graph = StateGraph(State)      # 그래프 생성
graph.add_node("이름", 함수)   # 노드 추가
graph.add_edge(A, B)           # 엣지 연결
app = graph.compile()          # 완성
app.invoke(초기상태)            # 실행
```

---

## 자주 헷갈리는 것들

### Q. StateGraph vs MessagesState 차이?
- `MessagesState` : LangGraph가 미리 만들어둔 간단한 상태 (메시지 목록만 있음)
- `StateGraph(나만의클래스)` : 내가 원하는 필드를 직접 정의한 상태 (예: `topic` 필드 추가)

### Q. MemorySaver는 껐다 켜면?
- RAM 저장이라 **프로그램 종료 시 사라짐**
- 영구 저장하려면 `SqliteSaver` 또는 `PostgresSaver` 사용

### Q. 노드 함수는 꼭 딕셔너리를 반환해야 하나요?
- 네! 항상 `{"상태키": 값}` 형태로 반환
- 반환한 값이 현재 상태에 **업데이트/추가**됨

---

## 핵심 요약 (3줄)

1. **LangGraph** = 노드(작업) + 엣지(경로) + 상태(메모장)로 AI 흐름 만들기
2. **MemorySaver + thread_id** = 대화방별 기억 구현
3. **add_conditional_edges** = 조건에 따라 다른 노드로 분기
