# LangChain Chain 핵심 요약

> **비유로 이해하기** : Chain은 **공장 컨베이어 벨트**입니다.  
> 원재료(입력) → 공정1 → 공정2 → 공정3 → 완성품(출력)

---

## 목차
1. [LCEL - 기본 체인](#1-lcel---기본-체인-1basicpy)
2. [RunnableLambda - 내 함수 끼워넣기](#2-runnablelambda---내-함수-끼워넣기-2runnablelambdapy)
3. [체인 연결하기 - 2단계 처리](#3-체인-연결하기---2단계-처리-3runnablelambda2py)
4. [RunnableParallel - 동시에 여러 작업](#4-runnableparallel---동시에-여러-작업-4runnableparallelpy)
5. [RunnableBranch - 조건 분기](#5-runnablebranch---조건-분기-5runnablebranchpy)
6. [RunnableBranch + Lambda - 디버깅](#6-runnablebranch--lambda---디버깅-6runnablebranch2py)

---

## 1. LCEL - 기본 체인 (`1.basic.py`)

### 핵심 개념: `|` 파이프 연산자

```
prompt | llm | parser
```

> **비유** : 물 파이프처럼 앞의 결과가 뒤로 흘러갑니다.

```python
chain = prompt | llm | parser
#       ↑        ↑     ↑
#    질문 만들기  AI   문자열로 변환
```

### 흐름 이해

```
입력값 {"company": "AI회사", "product": "화장품"}
  ↓
[prompt]  →  "AI회사에서 화장품을 만드는데 제품명을 만들어주세요"
  ↓
[llm]     →  AIMessage(content="에코글로우")  ← AI가 답변
  ↓
[parser]  →  "에코글로우"  ← 순수 문자열로 변환
```

### 핵심 3요소

| 구성요소 | 역할 | 비유 |
|---------|------|------|
| `ChatPromptTemplate` | 질문 틀 만들기 | 주문서 양식 |
| `ChatOpenAI` | AI가 답변 | 요리사 |
| `StrOutputParser` | 결과를 문자열로 | 포장지 제거 |

---

## 2. RunnableLambda - 내 함수 끼워넣기 (`2.runnablelambda.py`)

### 핵심 개념

> **비유** : 컨베이어 벨트 중간에 **내가 만든 공정**을 추가하는 것

```python
chain = prompt | llm | parser | RunnableLambda(lambda x: {"response": x})
#                                ↑
#                        내 함수를 체인에 끼워넣기
```

### 언제 쓰나?
- AI 응답을 **딕셔너리로 감쌀 때**
- 결과에 **내가 원하는 가공**을 추가할 때
- 중간 데이터를 **변환**할 때

### 흐름 이해

```
"에코글로우" (문자열)
  ↓
RunnableLambda(lambda x: {"response": x})
  ↓
{"response": "에코글로우"} (딕셔너리)
```

---

## 3. 체인 연결하기 - 2단계 처리 (`3.runnablelambda2.py`)

### 핵심 개념

> **비유** : 1공장 → 2공장으로 **반제품을 넘기는** 것

```
[1단계] 제품 → 회사명 생성
  ↓  (RunnableLambda로 포장)
[2단계] 회사명 → 캐치프레이즈 생성
```

### chain1 방식 (단순 순서 연결)

```python
chain1 = (
    prompt_name | llm | StrOutputParser()
    | RunnableLambda(lambda name: {"company_name": name.strip()})
    | prompt_slogan | llm | StrOutputParser()
    | RunnableLambda(lambda slogan: {"slogan": slogan.strip()})
)
```

### chain2 방식 (중간에 다른 체인 실행)

```python
chain2 = (
    prompt_name | llm | StrOutputParser()
    | RunnableLambda(lambda name: {"company_name": name.strip()})
    | RunnableLambda(lambda d: {
        "company_name": d["company_name"],
        "slogan": (prompt_slogan | llm | StrOutputParser()).invoke(...)
        #          ↑ 람다 안에서 다른 체인을 직접 실행
    })
)
```

### 두 방식 비교

| | chain1 | chain2 |
|--|--------|--------|
| 구조 | 단순 순서 연결 | 람다 안에서 체인 실행 |
| 최종 출력 | 슬로건 문자열만 | 회사명 + 슬로건 딕셔너리 |
| 용도 | 단순 흐름 | 여러 값을 같이 전달할 때 |

---

## 4. RunnableParallel - 동시에 여러 작업 (`4.runnableparallel.py`)

### 핵심 개념

> **비유** : 같은 원재료를 **여러 공장에 동시에** 보내는 것

```
"안녕하세요" ──┬──→ 영어 체인 → "Hello"
              ├──→ 중국어 체인 → "你好"
              ├──→ 일본어 체인 → "こんにちは"
              └──→ 프랑스어 체인 → "Bonjour"
```

### 코드 구조

```python
parallel_chain = RunnableParallel({
    "english": chain_en,   # 동시에 실행
    "chinese": chain_ch,   # 동시에 실행
    "japanese": chain_ja,  # 동시에 실행
    "franch": chain_fr     # 동시에 실행
})

result = parallel_chain.invoke({"text": "안녕하세요"})
# result = {
#   "english": "Hello",
#   "chinese": "你好",
#   "japanese": "こんにちは",
#   "franch": "Bonjour"
# }
```

### 장점
- 순서대로 실행하면 4번 기다려야 하지만, **동시 실행으로 시간 절약**
- 결과가 **딕셔너리로 묶여서** 한 번에 반환됨

---

## 5. RunnableBranch - 조건 분기 (`5.runnablebranch.py`)

### 핵심 개념

> **비유** : 상담 전화에서 **"1번: 기술 문의 / 2번: 요리 문의 / 0번: 일반"** 처럼 분기하는 것

```
질문 입력
  ↓
"파이썬" or "코드" 포함? → YES → 개발자 체인
  ↓ NO
"요리" or "레시피" 포함? → YES → 요리사 체인
  ↓ NO
기본 → 일반 어시스턴트 체인
```

### 코드 구조

```python
branch = RunnableBranch(
    (조건1_함수, 조건1이_True일때_실행할_체인),
    (조건2_함수, 조건2이_True일때_실행할_체인),
    기본_체인  # 아무 조건도 안 맞으면 실행
)
```

### 실제 예시

```python
branch = RunnableBranch(
    (lambda x: "파이썬" in x["question"], code_chain),    # 1순위 조건
    (lambda x: "요리" in x["question"],   cook_chain),    # 2순위 조건
    general_chain                                         # 기본값
)
```

> **주의** : 조건은 **위에서부터 순서대로** 확인합니다. 먼저 True가 되는 체인이 실행됩니다.

---

## 6. RunnableBranch + Lambda - 디버깅 (`6.runnablebranch2.py`)

### 핵심 개념

> **비유** : 공장 입구에 **CCTV(로그)** 를 달아서 어느 공정으로 들어가는지 확인하는 것

```python
code_chain = (
    RunnableLambda(lambda x: print(">>> 개발자 코드 실행") or x)
    #              ↑ 실행 확인용 출력 (그리고 x를 그대로 다음으로 전달)
    | make_chain("당신은 파이썬 개발자입니다.")
)
```

### `print(...) or x` 패턴 이해

```python
lambda x: print("로그") or x
#          ↑             ↑
#      출력 (None 반환)  None or x = x 반환
```
- `print()`는 항상 `None`을 반환
- `None or x` = `x` (원본 데이터 그대로 통과)

### 심화 문제: "된장찌개 파이썬 레시피"는 어디로?

```python
"된장찌개 파이썬 레시피 알려줘"
```

- `"파이썬" in question` → **True** ← 1순위 조건 먼저 통과!
- `"요리" in question` → True (but 이미 위에서 결정됨)

**결과: 개발자 체인 실행** (조건은 위에서부터 순서대로!)

---

## 전체 개념 한눈에 보기

```
┌─────────────────────────────────────────────────────┐
│                  LangChain Chain 종류                │
├──────────────────┬──────────────────────────────────┤
│ LCEL (|)         │ 기본 파이프라인 연결              │
│ RunnableLambda   │ 내 함수를 체인에 끼워넣기         │
│ RunnableParallel │ 여러 체인을 동시에 실행           │
│ RunnableBranch   │ 조건에 따라 다른 체인 실행        │
└──────────────────┴──────────────────────────────────┘
```

## 자주 쓰는 패턴 요약

```python
# 1. 기본 체인
chain = prompt | llm | StrOutputParser()

# 2. 중간에 변환 추가
chain = prompt | llm | StrOutputParser() | RunnableLambda(lambda x: {"result": x})

# 3. 동시 실행
chain = RunnableParallel({"a": chain1, "b": chain2})

# 4. 조건 분기
chain = RunnableBranch(
    (lambda x: 조건, 체인A),
    체인B  # 기본값
)
```
