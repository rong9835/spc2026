# LangChain 실전 Tasks 핵심 요약

> 📌 이 폴더는 LangChain으로 실제 업무를 자동화하는 6가지 실습입니다.
> 초보자도 이해할 수 있도록 **비유**와 함께 설명합니다.

---

## 🗂 전체 목차

| 파일 | 기능 | 핵심 개념 |
|------|------|-----------|
| `1.summary.py` | 긴 글 요약 | Chain + RunnableLambda |
| `2.emailgen.py` | 이메일 자동 생성 | StrOutputParser + 반복 |
| `3.sqlgen.py` | SQL 자동 생성 | temperature=0 (정확도 우선) |
| `4.news.py` | 뉴스 동시 분석 | RunnableParallel (병렬 실행) |
| `5.callcenter.py` | 콜센터 자동 분류 | RunnableBranch (조건 분기) |
| `6.tripplanner.py` | 여행 계획 생성 | Parallel + Branch 결합 |

---

## 📄 1. 문장 요약기 (`1.summary.py`)

### 무엇을 하나요?
긴 뉴스 기사를 AI에게 주면 → **3문장으로 짧게 요약**해줍니다.

### 핵심 코드 흐름
```
입력(article) → 프롬프트 → LLM → 결과 정리(lambda)
```

```python
chain = chat_prompt | llm | RunnableLambda(lambda x: {"summary": x.content.strip()})
```

### 비유로 이해하기
> 🍱 도시락처럼 **재료(입력) → 조리(LLM) → 포장(lambda)** 순서로 처리됩니다.

### 핵심 포인트
- `SystemMessage`: AI의 역할 설정 ("넌 요약 전문가야")
- `HumanMessage`: 실제 사용자 요청 ("이걸 요약해줘")
- `temperature=0.5`: 창의성 중간 값 (요약엔 너무 창의적이면 안 됨)
- `RunnableLambda`: 결과를 원하는 형태로 변환하는 함수

---

## 📧 2. 이메일 자동 생성기 (`2.emailgen.py`)

### 무엇을 하나요?
수신자와 주제만 입력하면 → **전문적인 이메일을 자동으로 작성**해줍니다.

### 핵심 코드 흐름
```
(수신자, 주제) → 프롬프트 → LLM → StrOutputParser → 이메일 텍스트
```

```python
chain = chat_prompt | llm | StrOutputParser()

for recipient, topic in zip(recipients, topics):
    result = chain.invoke({"recipient": recipient, "topic": topic})
```

### 비유로 이해하기
> 📮 편지 자판기처럼 **받는 사람과 용건만 누르면** 완성된 편지가 나옵니다.

### 핵심 포인트
- `StrOutputParser()`: 결과를 순수한 **문자열**로만 반환 (딕셔너리 없이)
- `temperature=0.7`: 이메일은 약간의 창의성이 필요하므로 중간~높게 설정
- `max_tokens=1000`: 이메일이 너무 길어지지 않도록 최대 길이 제한
- `zip()`: 두 리스트를 짝지어서 하나씩 처리

---

## 🗄 3. SQL 자동 생성기 (`3.sqlgen.py`)

### 무엇을 하나요?
테이블 구조(Schema)와 한국어 질문을 주면 → **SQL 쿼리를 자동으로 생성**해줍니다.

### 핵심 코드 흐름
```
(스키마 + 질문) → 프롬프트 → LLM → SQL 결과
```

```python
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # 정확도 최우선!
```

### 비유로 이해하기
> 🗺 "강남역 근처 카페 찾아줘"라고 말하면 → GPS가 **정확한 경로**를 알려주는 것처럼,
> 자연어 질문을 **정확한 SQL 명령어**로 변환해줍니다.

### 핵심 포인트
- `temperature=0`: SQL은 **정답이 하나**이므로 창의성 없이 정확하게
- `DB Schema`: AI에게 테이블 구조를 알려줘야 올바른 SQL을 생성할 수 있음
- `"SQL 쿼리문으로만 답변"`: 시스템 프롬프트로 불필요한 설명 차단

### 사용된 테이블
```
users 테이블: id, name, email, signup_date
orders 테이블: id, user_id, product_name, price, created_at
```

---

## 📰 4. 뉴스 분석기 (`4.news.py`) ⭐ 중요

### 무엇을 하나요?
뉴스 1개를 입력하면 → **요약, 감성 분석, 카테고리**를 **동시에** 분석합니다.

### 핵심 코드 흐름
```
뉴스 입력 ──┬─→ 요약 체인    → 요약 결과
            ├─→ 감성 체인    → 긍정/부정/중립
            └─→ 카테고리 체인 → IT/경제/사회 등
```

```python
final_chain = RunnableParallel({
    "summary": summary_chain,
    "sentiment": sentiment_chain,
    "category": category_chain,
})
```

### 비유로 이해하기
> 🏭 공장 컨베이어 벨트처럼 같은 재료(뉴스)를 여러 작업자가 **동시에** 처리합니다.
> 순서대로 하면 3배 걸리지만, 동시에 하면 **1배 시간**만 걸립니다!

### 핵심 포인트
- `RunnableParallel`: 여러 체인을 **동시에(병렬로)** 실행
- 결과는 딕셔너리로 반환: `{"summary": ..., "sentiment": ..., "category": ...}`
- 순차 실행보다 **빠름** (API 호출이 동시에 이뤄짐)

---

## 📞 5. 콜센터 자동 분류기 (`5.callcenter.py`) ⭐ 중요

### 무엇을 하나요?
고객 질문을 분석해서 → **적합한 상담원(체인)으로 자동 연결**합니다.

### 핵심 코드 흐름
```
고객 질문 → 키워드 확인 ─┬─ "결제/환불/청구" 포함 → 결제 상담원
                         ├─ "배송/택배/반품" 포함 → 배송 상담원
                         ├─ "오류/에러/안돼요" 포함 → 기술 지원
                         └─ (해당 없음)           → 일반 상담원
```

```python
branch = RunnableBranch(
    (lambda x: any(k in x["question"] for k in ["결제", "환불", "청구"]), payment_chain),
    (lambda x: any(k in x["question"] for k in ["배송", "택배", "반품"]), delivary_chain),
    (lambda x: any(k in x["question"] for k in ["오류", "에러", "안돼요"]), techsupport_chain),
    general_chain,  # ← 어디에도 안 걸리면 여기로
)
```

### 비유로 이해하기
> 🚦 신호등처럼 **조건에 따라 방향을 결정**합니다.
> "결제"라는 단어가 있으면 → 결제 담당자에게 연결!

### 핵심 포인트
- `RunnableBranch`: **조건(if-else)에 따라 다른 체인 실행**
- `lambda x: any(k in ...)`: 키워드 하나라도 포함되면 해당 체인으로 이동
- 마지막 인자(기본값): 어느 조건도 맞지 않을 때 실행되는 체인
- `make_chain(role)`: 역할만 다르고 구조가 같은 체인을 함수로 재사용

---

## ✈️ 6. 여행 계획기 (`6.tripplanner.py`)

### 무엇을 하나요?
도시를 입력하면 → **음식 추천, 관광지 추천, 호텔 추천**을 동시에 생성합니다.

> 💡 `RunnableParallel`과 `RunnableBranch`를 결합한 종합 실습입니다.

---

## 🧩 핵심 개념 총정리

### LangChain의 3가지 파이프 연산자

```
프롬프트 | LLM | 출력파서
```

> 파이프(`|`)는 **물이 흐르듯** 앞 단계 결과가 다음 단계로 전달됩니다.

---

### 출력 파서 비교

| 파서 | 반환 형태 | 사용 상황 |
|------|-----------|-----------|
| `StrOutputParser()` | 순수 문자열 `"..."` | 텍스트 그대로 출력할 때 |
| `RunnableLambda(fn)` | 함수 결과 (자유) | 딕셔너리 등 커스텀 형태 필요할 때 |

---

### temperature 설정 가이드

| 값 | 특성 | 사용 예시 |
|----|------|-----------|
| `0` | 항상 동일한 정답 | SQL 생성, 코드 생성 |
| `0.3~0.5` | 약간의 변화 | 요약, 분석 |
| `0.7~1.0` | 창의적 다양성 | 이메일, 글쓰기 |

---

### 실행 방식 비교

```
순차 실행 (Chain)          병렬 실행 (RunnableParallel)
────────────────          ──────────────────────────
입력 → A → B → C          입력 ─┬─→ A → 결과A
(A 끝나야 B 시작)                ├─→ B → 결과B
                                 └─→ C → 결과C
                          (A, B, C 동시 시작!)

조건 실행 (RunnableBranch)
──────────────────────────
입력 → 조건1? → 체인1
      조건2? → 체인2
      기본  → 기본체인
```

---

## 🚀 실습 순서 추천

1. `1.summary.py` → Chain 기본 구조 이해
2. `2.emailgen.py` → 반복 호출 패턴 이해
3. `3.sqlgen.py` → temperature 설정의 중요성 이해
4. `4.news.py` → **RunnableParallel** 이해 (병렬 처리)
5. `5.callcenter.py` → **RunnableBranch** 이해 (조건 분기)
6. `6.tripplanner.py` → 두 개념 결합 응용
