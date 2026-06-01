# LangChain 프롬프트 핵심 요약

> AI에게 질문을 보내는 방법을 단계별로 배웁니다.

---

## 전체 흐름 한눈에 보기

```
입력값 → [프롬프트 템플릿] → [LLM(AI)] → [출력 파서] → 결과
```

마치 **편지 양식**처럼: 빈칸만 채우면 완성된 질문이 만들어지고, AI가 답변하고, 원하는 형태로 정리됩니다.

---

## 1. PromptTemplate — 기본 프롬프트 틀 만들기
> `1.template_legacy.py`

```python
from langchain_core.prompts import PromptTemplate

template = "당신은 작명가입니다. 상품명: {product} 회사 이름을 지어주세요."
prompt = PromptTemplate(input_variables=['product'], template=template)

filled = prompt.format(product="스마트폰")
# → "당신은 작명가입니다. 상품명: 스마트폰 회사 이름을 지어주세요."
```

**핵심 개념**
- `{product}` 처럼 `{}` 안에 변수명을 넣으면 **빈칸**이 됩니다
- `.format(product="스마트폰")` 으로 빈칸을 채웁니다
- 여러 상품에 같은 틀을 재사용할 수 있어요

---

## 2. ChatPromptTemplate — 채팅형 프롬프트
> `2.template_chat.py`

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 작명가입니다."),          # AI의 역할 설정
    ("user",   "상품명: {product} 회사 이름을 지어주세요.")  # 사용자 질문
])

messages = prompt.format_messages(product="자율주행 자동차")
```

**PromptTemplate vs ChatPromptTemplate 차이점**

| | PromptTemplate | ChatPromptTemplate |
|---|---|---|
| 형태 | 문자열 하나 | 메시지 목록 |
| 역할 구분 | 없음 | system / user / ai 구분 |
| 사용 상황 | 단순 텍스트 | 대화형 AI (GPT 등) |

**메시지 역할 3가지**
- `system` — AI에게 **역할**을 부여 ("너는 브랜드 기획자야")
- `user` — **사람이 하는 말** ("이것 좀 해줘")
- `ai` — **AI가 했던 말** (대화 히스토리에 활용)

---

## 3. LLM 호출 — AI에게 실제로 물어보기
> `3.template_invoke.py`

```python
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()                              # .env 파일에서 API 키 불러오기
llm = ChatOpenAI(model="gpt-4o-mini")     # AI 모델 선택

filled_prompt = prompt.format_messages(product="자율주행 자동차")
response = llm.invoke(filled_prompt)       # AI 호출!

print(response.content)                    # 답변 출력
```

**흐름 정리**
```
.env (API 키) → ChatOpenAI → .invoke(프롬프트) → response.content
```

---

## 4. Output Parser — 결과를 원하는 형태로 변환
> `4.output_parser.py`

```python
from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers import CommaSeparatedListOutputParser

parser1 = StrOutputParser()               # 일반 문자열로
parser2 = CommaSeparatedListOutputParser() # 리스트로 (콤마 구분)

result_str  = parser1.invoke(response)    # "캐치프레이즈1, 캐치프레이즈2, ..."
result_list = parser2.invoke(response)    # ["캐치프레이즈1", "캐치프레이즈2", ...]
```

**비유**: AI가 답변을 돌려줄 때 **상자(response) 그대로**가 아니라  
원하는 모양(문자열, 리스트 등)으로 **꺼내주는 도구**가 파서입니다.

---

## 5. 수동 체인 — 단계별로 직접 실행
> `5.langchain.py`

```python
# 단계 1: 프롬프트 완성
messages = prompt.format_messages(**inputs)

# 단계 2: AI 호출
response = llm.invoke(messages)

# 단계 3: 파싱
output = parser.invoke(response)
```

각 단계를 **직접 순서대로** 실행합니다. 이해하기 쉽지만 코드가 길어집니다.

---

## 6. LCEL — 파이프(|)로 연결하기 ⭐ 핵심!
> `6.langchain_lcel.py`

```python
# 수동 방식
messages  = prompt.format_messages(**inputs)
response  = llm.invoke(messages)
output    = parser.invoke(response)

# LCEL 방식 (똑같은 동작!)
chain = prompt | llm | parser      # 파이프로 연결
result = chain.invoke(inputs)       # 한 번에 실행
```

**LCEL(LangChain Expression Language)**
- `|` 기호는 **"앞 결과를 다음으로 넘긴다"** 는 뜻
- 마치 **공장 컨베이어 벨트**처럼: 프롬프트 → AI → 파서 순서로 흘러갑니다
- 코드가 훨씬 짧고 읽기 쉬워집니다

---

## 7. RunnableLambda — 체인에 내 함수 끼워넣기
> `7.langchain_lcel2.py`

```python
from langchain_core.runnables import RunnableLambda

chain = prompt | llm | parser | RunnableLambda(lambda x: {"response": x})
result = chain.invoke(inputs)
# → {"response": "캐치프레이즈 내용..."}
```

**언제 쓰나요?**  
체인 중간이나 끝에 **내가 만든 함수**를 넣고 싶을 때 사용합니다.  
`lambda x: ...` 는 "x를 받아서 이렇게 바꿔줘" 라는 뜻입니다.

---

## 8. FewShot — 예시를 보여주고 따라하게 하기
> `8.fewshot.py`

```python
from langchain_core.prompts import FewShotPromptTemplate

examples = [
    {"sentence": "오늘 정말 최고의 하루였어!", "result": "감정: 긍정 / 점수: 9"},
    {"sentence": "이거 진짜 별로네요.",         "result": "감정: 부정 / 점수: 2"},
    # ...
]

fewshot_prompt = FewShotPromptTemplate(
    examples=examples,           # 예시 목록
    example_prompt=example_prompt, # 예시 포맷
    prefix="...",                # 예시 앞 설명
    suffix="문장: {sentence}\n분석:",  # 실제 질문
    input_variables=["sentence"],
)
```

**퓨샷(Few-Shot)이란?**  
AI에게 **몇 가지 예시를 먼저 보여주고** 같은 방식으로 답하게 만드는 기법입니다.

```
예시 없이 물어볼 때:  자유롭게 답변 (형식 제각각)
예시 보여주고 물어볼 때: 예시 형식 그대로 답변 ✓
```

---

## 전체 진화 흐름 정리

```
1단계  PromptTemplate           문자열 빈칸 채우기
   ↓
2단계  ChatPromptTemplate       system/user 역할 분리
   ↓
3단계  + LLM                    AI 실제 호출
   ↓
4단계  + OutputParser           결과 형태 변환
   ↓
5단계  수동 체인                 단계별 직접 실행
   ↓
6단계  LCEL (prompt | llm | parser)  파이프로 깔끔하게 연결 ⭐
   ↓
7단계  + RunnableLambda         내 함수도 체인에 추가
   ↓
8단계  FewShotPromptTemplate    예시 기반 고품질 응답
```

---

## 자주 쓰는 코드 패턴 (복붙용)

```python
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# 1. 프롬프트 정의
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 {role}입니다."),
    ("user", "{question}")
])

# 2. 모델 + 파서
llm    = ChatOpenAI(model="gpt-4o-mini")
parser = StrOutputParser()

# 3. 체인 연결
chain = prompt | llm | parser

# 4. 실행
result = chain.invoke({"role": "작명가", "question": "스마트폰 회사 이름 추천해줘"})
print(result)
```
