# LangChain Output Parsers (출력 파서)

> AI가 대답을 돌려줄 때, **원하는 형태로 정리해주는 도구**가 Output Parser입니다.

---

## 핵심 개념 한 줄 요약

```
프롬프트 → AI → Output Parser → 내가 원하는 형태의 결과
```

AI는 항상 **텍스트(문자열)** 로 대답합니다.  
하지만 우리는 때로는 리스트, 딕셔너리, 객체 형태가 필요하죠.  
→ Output Parser가 텍스트를 원하는 형태로 **변환**해줍니다.

---

## 1. StrOutputParser — 문자열 그대로 받기

📄 파일: `1.str_parser.py`

### 이런 상황에 사용
AI 대답을 **그냥 텍스트**로 받고 싶을 때

### 코드 패턴
```python
from langchain_core.output_parsers import StrOutputParser

chain = prompt | llm | StrOutputParser()
result = chain.invoke({"product": "웹게임"})
# result의 타입: str (문자열)
```

### CommaSeparatedListOutputParser — 리스트로 받기
쉼표로 구분된 대답을 **파이썬 리스트**로 자동 변환

```python
from langchain_core.output_parsers import CommaSeparatedListOutputParser

chain = prompt | llm | CommaSeparatedListOutputParser()
result = chain.invoke({"topic": "인공지능"})
# result의 타입: list (리스트)
# 예: ['머신러닝', '딥러닝', '자연어처리', '컴퓨터비전', '강화학습']
```

### 체인 연결 (핵심!)
두 체인을 이어붙이기 — 첫 번째 결과를 두 번째 입력으로 전달

```python
chain = (
    prompt_name        # 1단계: 회사 이름 만들기
    | llm
    | StrOutputParser()
    | (lambda name: {"company_name": name.strip()})  # 결과를 다음 프롬프트 입력으로 변환
    | prompt_slogan    # 2단계: 그 이름으로 캐치프레이즈 만들기
    | llm
    | StrOutputParser()
)
```

> 비유: 공장 컨베이어 벨트처럼, 앞 작업 결과가 다음 작업 재료가 됩니다.

---

## 2. PydanticOutputParser — 클래스(객체)로 받기

📄 파일: `2.pydantic.py`

### 이런 상황에 사용
AI 대답을 **미리 정의한 구조체(클래스)** 형태로 받고 싶을 때

### 핵심 흐름

```
1. 클래스 정의 (어떤 필드가 있는지)
   ↓
2. PydanticOutputParser 생성
   ↓
3. AI에게 "이 형식으로 답해줘" 라고 자동으로 지시
   ↓
4. AI 대답을 클래스 객체로 변환
```

### 코드 패턴
```python
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

# 1단계: 원하는 구조 정의
class MovieReview(BaseModel):
    title: str = Field(description="영화 제목")
    sentiment: str = Field(description="감성: 긍정/부정/중립")
    score: int = Field(description="1~10 점수")
    summary: str = Field(description="요약 1~2문장")
    keywords: list[str] = Field(description="핵심 키워드 3개")

# 2단계: 파서 생성
parser = PydanticOutputParser(pydantic_object=MovieReview)

# 3단계: 프롬프트에 포맷 지시사항 포함
prompt = ChatPromptTemplate.from_template("""
리뷰: {review}
{format_instructions}
""")

chain = prompt | llm | parser

# 4단계: 결과 사용 (클래스 필드로 접근 가능!)
result = chain.invoke({"review": "...", "format_instructions": parser.get_format_instructions()})
print(result.title)      # 영화 제목
print(result.score)      # 점수 (int)
print(result.keywords)   # 키워드 (list)
```

> 비유: AI에게 "이 양식지에 맞춰서 작성해줘" 하고 양식지를 주는 것과 같습니다.

---

## 3. JsonOutputParser — 딕셔너리(JSON)로 받기

📄 파일: `3.json_parser.py`

### 이런 상황에 사용
AI 대답을 **파이썬 딕셔너리** 형태로 받고 싶을 때

### 코드 패턴
```python
from langchain_core.output_parsers import JsonOutputParser

parser = JsonOutputParser()

prompt = ChatPromptTemplate.from_messages([
    ("system", "답변은 항상 JSON으로만 하시오."),
    ("user", "{question}\n\n{format_instruction}")
]).partial(format_instruction=parser.get_format_instructions())
#   ↑ .partial()로 고정값을 미리 채워두면
#     나중에 question만 넣어도 됩니다

chain = prompt | llm | parser

result = chain.invoke({"question": "아시아 인구 상위 3개국과 수도는?"})
# result의 타입: dict (딕셔너리)
```

> `.partial()` 포인트: 자주 변하지 않는 값은 미리 고정해두면 편리합니다.

---

## 세 가지 파서 비교표

| 파서 | 결과 타입 | 언제 사용? |
|------|-----------|------------|
| `StrOutputParser` | `str` (문자열) | 그냥 텍스트로 받을 때 |
| `CommaSeparatedListOutputParser` | `list` (리스트) | 쉼표 구분 목록이 필요할 때 |
| `PydanticOutputParser` | 클래스 객체 | 정해진 구조가 필요할 때 |
| `JsonOutputParser` | `dict` (딕셔너리) | 유연한 JSON이 필요할 때 |

---

## 전체 패턴 암기법

```
chain = prompt | llm | 파서
result = chain.invoke(입력값)
```

- `|` 기호는 "그 다음에" 라는 의미 (파이프라인)
- `invoke()` = "실행해줘"
- 파서는 항상 마지막에 붙임

---

## 자주 묻는 질문

**Q. Pydantic이 뭔가요?**  
A. 파이썬에서 데이터 구조를 안전하게 정의하는 라이브러리입니다. 타입이 틀리면 자동으로 오류를 잡아줍니다.

**Q. PydanticParser vs JsonParser 차이는?**  
A. Pydantic은 클래스로 정의된 **고정 구조**, JSON은 자유로운 **유연한 구조**입니다.  
→ 필드가 정해져 있으면 Pydantic, 그렇지 않으면 JSON 사용.

**Q. `format_instructions`는 뭔가요?**  
A. AI에게 "이런 형식으로 답해줘" 하고 알려주는 지시문입니다. 파서가 자동으로 만들어줍니다.
