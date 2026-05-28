# LangChain 완전 초보자 가이드

---

## LangChain이 뭐야?

ChatGPT 같은 AI를 **파이썬 코드로 조종하는 도구**예요.

> **비유로 이해하기**
> - ChatGPT 웹사이트 = 사람이 직접 타자 치는 것
> - LangChain = **코드로 자동으로** AI한테 질문하고 답변 받는 것

---

## 핵심 개념 3가지

LangChain은 딱 3가지만 알면 돼요.

```
1. 프롬프트  →  2. AI 모델  →  3. 파서
(질문 만들기)    (AI가 답변)    (답변 가공)
```

**카페에 비유하면:**
- 프롬프트 = 주문서 ("아이스 아메리카노 한 잔")
- AI 모델 = 바리스타 (커피 만드는 사람)
- 파서 = 트레이 (커피를 예쁘게 담아서 전달)

---

## 1단계 - AI 모델 연결하기 (`1.basic`)

### OpenAI vs ChatOpenAI

```python
from langchain_openai import OpenAI      # 단순 질문용
from langchain_openai import ChatOpenAI  # 대화용 (주로 이걸 씀)
```

**차이가 뭐야?**

| | OpenAI | ChatOpenAI |
|--|--------|------------|
| 비유 | 자판기 (버튼 누르면 바로 나옴) | 점원 (역할을 알려주고 대화 가능) |
| 용도 | 번역, 단순 답변 | 챗봇, 역할 부여 |

### 메시지 3종류

ChatOpenAI에 보낼 때는 **누가 말하는지** 지정해줘야 해요.

```python
SystemMessage  # AI한테 "넌 이런 역할이야" 설명해주는 것
HumanMessage   # 사람(나)이 하는 말
AIMessage      # AI가 이전에 한 말 (대화 기록)
```

**실제 예시:**
```python
prompt = [
    SystemMessage(content="당신은 경력 10년 호텔 쉐프입니다."),  # 역할 설정
    HumanMessage(content="오늘 저녁 메뉴 추천해줘."),            # 내 질문
    AIMessage(content="비빔밥은 어떠신가요?"),                    # AI 이전 답변
    HumanMessage(content="아~ 좋아. 그 재료는?"),                 # 다음 내 질문
]
```

> 마치 카카오톡 대화 내역을 통째로 AI한테 보내주는 느낌이에요.

---

## 2단계 - 프롬프트 템플릿 (`2.prompt`)

### 왜 필요해?

매번 질문을 직접 쓰면 불편하잖아요.  
변수만 바꿔서 **같은 형식의 질문을 반복**할 때 쓰는 틀이에요.

**비유:** 편지 양식 같은 것

```
받는 분: {이름}
내용: {내용} 에 대한 미팅을 요청드립니다.
```

**코드로 보면:**
```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 작명가입니다."),
    ("user", "{product} 회사 이름을 지어주세요.")  # {product}가 변수
])

# 변수에 값 넣기
messages = prompt.format_messages(product="스마트폰")
messages = prompt.format_messages(product="자율주행 자동차")
```

이렇게 하면 `{product}` 자리에 원하는 값을 계속 바꿔넣을 수 있어요!

### FewShot - 예시를 보여줘서 형식 맞추기

> **비유:** "이런 식으로 답해줘" 하고 예시를 먼저 보여주는 것

```python
# 예시 5개를 보여주면서...
examples = [
    {"sentence": "오늘 최고의 하루!", "result": "감정: 긍정 / 점수: 9"},
    {"sentence": "별로였어요.",       "result": "감정: 부정 / 점수: 2"},
]

# "이 패턴대로 새 문장도 분석해줘" 라고 요청하는 것
```

예시를 안 줬을 때보다 훨씬 일관된 형식으로 답변이 나와요.

---

## 3단계 - LCEL과 체인 (`2.prompt`, `4.chain`)

### LCEL이 뭐야?

**LCEL = LangChain Expression Language**

LangChain에서 만든 **특별한 연결 문법**이에요.  
`|` (파이프) 기호 하나로 프롬프트 → AI → 파서를 이어붙이는 거예요.

> **비유:** 공장 컨베이어 벨트
> 원재료 → 가공 → 포장 → 완성품
>
> 각 단계를 `|` 로 이어주면, `invoke` 할 때 알아서 순서대로 실행돼요.

### LCEL 쓰기 전 vs 후

**LCEL 없이 쓸 때 (옛날 방식)**
```python
# 각각 따로따로 호출해야 함
messages = prompt.format_messages(company="하이닉스", product="HBM")
response = llm.invoke(messages)
output = parser.invoke(response)
final = {"response": output}
```

**LCEL 쓸 때 (현재 방식)**
```python
# | 로 이어붙이고 invoke 한 번이면 끝!
chain = prompt | llm | parser
result = chain.invoke({"company": "하이닉스", "product": "HBM"})
```

훨씬 짧고 읽기 쉽죠? 이게 LCEL의 핵심이에요.

### LCEL 기본 구조

```python
chain = prompt | llm | parser
#       ①        ②     ③
# ① 프롬프트 템플릿: 질문 만들기
# ② llm: AI가 답변
# ③ parser: 답변을 원하는 형태로 변환
```

### RunnableLambda - 중간에 내 코드 끼워넣기

LCEL 체인 중간에 **내가 원하는 코드를 끼워넣을 때** 써요.

> **비유:** 컨베이어 벨트 중간에 내가 직접 뭔가 손을 보는 것

```python
from langchain_core.runnables import RunnableLambda

# 파서 결과를 딕셔너리로 감싸고 싶을 때
chain = prompt | llm | parser | RunnableLambda(lambda x: {"response": x})
#                                ↑ 여기가 내 코드. x는 파서 결과물
```

### 체인을 2단계로 이어붙이기

> **비유:** 1공장 결과물이 2공장 원재료가 되는 것

```
입력: "에코백"
  ↓
1단계: "에코백 회사 이름은?" → AI → "그린어스"
  ↓  (RunnableLambda로 {"company_name": "그린어스"} 형태로 변환)
2단계: "그린어스 슬로건 만들어줘" → AI → "지구를 위한 선택"
  ↓
최종 결과: "지구를 위한 선택"
```

```python
chain = (
    prompt_name                                             # 1. 회사명 질문 만들기
    | llm                                                   # 2. AI가 회사명 답변
    | StrOutputParser()                                     # 3. 텍스트로 변환
    | RunnableLambda(lambda name: {"company_name": name})  # 4. 다음 입력 형태로 변환 ← 핵심!
    | prompt_slogan                                         # 5. 슬로건 질문 만들기
    | llm                                                   # 6. AI가 슬로건 답변
    | StrOutputParser()                                     # 7. 텍스트로 변환
)
```

---

## 4단계 - 출력 파서 (`3.output`)

AI 답변은 기본적으로 **그냥 긴 텍스트**예요.  
파서는 이걸 **원하는 형태로 바꿔주는 도구**예요.

| 파서 | 결과 형태 | 언제 써? |
|------|-----------|---------|
| `StrOutputParser` | "일반 텍스트" | 그냥 문자열이 필요할 때 |
| `CommaSeparatedListOutputParser` | `["A", "B", "C"]` | 목록으로 받고 싶을 때 |
| `JsonOutputParser` | `{"key": "value"}` | 딕셔너리로 받고 싶을 때 |
| `PydanticOutputParser` | 내가 만든 클래스 | 정해진 구조로 받고 싶을 때 |

**Pydantic 예시 - "이 형식대로 줘!" 강제하기**

```python
class MovieReview(BaseModel):
    title: str      # 영화 제목 (문자열)
    score: int      # 점수 (숫자)
    summary: str    # 요약

# AI가 아무리 말이 많아도 title, score, summary 딱 3개만 뽑아줌
result = chain.invoke({"review": "영화 리뷰 텍스트..."})
print(result.title)   # "Project Hail Mary"
print(result.score)   # 9
```

---

## 5단계 - 고급 체인 패턴 (`4.chain`)

### RunnableParallel - 동시에 여러 작업

> **비유:** 번역 회사에 한 문서를 주면서 영어/중국어/일본어 **동시에** 번역 요청

```
입력: "안녕하세요"
  ↓  ↓  ↓  ↓ (동시에!)
영어 | 중국어 | 일본어 | 프랑스어
  ↓  ↓  ↓  ↓
결과: {"english": "Hello", "chinese": "你好", ...}
```

순서대로 하면 4번 기다려야 하지만, Parallel은 **한 번에** 끝나요!

### RunnableBranch - 상황에 따라 다른 체인

> **비유:** 고객센터 자동 연결 시스템
> - "결제" 관련 → 결제팀 연결
> - "배송" 관련 → 배송팀 연결
> - 그 외 → 일반 상담팀

```python
branch = RunnableBranch(
    (lambda x: "파이썬" in x["question"], code_chain),  # 코드 질문 → 개발자 AI
    (lambda x: "요리" in x["question"],   cook_chain),  # 요리 질문 → 요리사 AI
    general_chain                                         # 그 외 → 일반 AI
)
```

---

## 6단계 - 실전 활용 (`5.tasks`)

배운 것들로 실제로 뭘 만들 수 있는지 예시예요.

### 텍스트 요약기 (`1.summary.py`)
긴 뉴스 기사 → AI → 3문장으로 요약

### 이메일 자동 생성기 (`2.emailgen.py`)
수신자 + 주제 입력 → AI → 전문적인 이메일 작성

### SQL 자동 생성기 (`3.sqlgen.py`)
"2023년 이후 가입한 유저 보여줘" → AI → `SELECT * FROM users WHERE...`

> SQL Generator는 `temperature=0` 으로 설정!
> temperature = AI의 창의성 수치 (0이면 항상 정확한 답, 1이면 창의적)

### 앞으로 만들 것들
- `4.news.py` → 뉴스 요약 + 감정분석 + 카테고리 동시 분석 (Parallel 활용)
- `5.callcenter.py` → 질문 유형별 상담원 자동 연결 (Branch 활용)
- `6.tripplanner.py` → 도시 입력하면 음식/관광지/호텔 동시 추천 (Parallel + Branch)

---

## 전체 흐름 한 장 요약

```
[내가 원하는 것]
       ↓
프롬프트 템플릿  ← {변수} 자리에 값 채우기
       ↓
  AI 모델       ← ChatOpenAI가 답변 생성
       ↓
  출력 파서     ← 텍스트를 리스트/JSON/객체로 변환
       ↓
[최종 결과]


더 복잡한 경우:
- 동시에 여러 작업 → RunnableParallel
- 조건에 따라 다른 처리 → RunnableBranch
- 결과를 다음 입력으로 → 체인 이어붙이기
```

---

## 설치 방법

```bash
pip install langchain langchain-openai python-dotenv
```

`.env` 파일에 API 키 저장:
```
OPENAI_API_KEY=sk-여기에_키_입력
```
