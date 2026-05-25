# Ollama 로컬 LLM 실습 정리

> 내 컴퓨터에서 AI를 무료로 돌리는 방법!

---

## Ollama란?

ChatGPT 같은 AI를 **내 컴퓨터(로컬)에서 무료로** 실행할 수 있게 해주는 프로그램입니다.

```
일반 AI 사용법:
나 → 인터넷 → OpenAI 서버 → 응답 (돈 듦)

Ollama 사용법:
나 → 내 컴퓨터 → 응답 (무료!)
```

---

## 준비 설치 (한 번만 하면 됨)

```bash
# 1. Ollama 설치 (홈페이지에서 다운로드)
# https://ollama.com

# 2. AI 모델 다운로드 (USB처럼 모델을 내 컴퓨터에 저장)
ollama pull qwen2.5:1.5b      # 중국 Alibaba AI (작고 빠름)
ollama pull exaone3.5:2.4b    # LG AI 모델

# 3. Python 라이브러리 설치
pip install requests
pip install faiss-cpu
```

---

## 파일 1: `1.qwen.py` — 기본 채팅봇

### 핵심 개념

Ollama는 내 컴퓨터 안에서 조용히 실행되고 있고,  
Python은 그 Ollama한테 **편지(HTTP 요청)** 를 보내서 답장을 받습니다.

```
Python → (편지) → Ollama(내 컴퓨터 localhost:11434) → (답장) → Python
```

### 코드 흐름

```python
import requests

MODEL_NAME = "exaone3.5:latest"   # 사용할 AI 모델 이름

def ask_qwen(question):
    # Ollama에 POST 요청 보내기 (편지 보내기)
    response = requests.post(
        "http://localhost:11434/api/generate",  # Ollama 주소 (내 컴퓨터)
        json={
            "model": MODEL_NAME,   # 어떤 AI 쓸지
            "prompt": question,    # 질문 내용
            "stream": False        # 한 번에 전체 답장 받기
        }
    )
    data = response.json()
    return data['response']        # 답장에서 응답 텍스트만 꺼내기

# 무한 대화 루프
while True:
    user_input = input("나: ")
    if user_input == "exit":       # exit 입력하면 종료
        break
    print("응답:", ask_qwen(user_input))
```

### 핵심 포인트 요약

| 항목 | 설명 |
|------|------|
| `localhost:11434` | 내 컴퓨터에서 실행 중인 Ollama 주소 |
| `requests.post()` | Ollama에 질문을 HTTP로 전달 |
| `"stream": False` | 스트리밍 없이 완성된 답변을 한 번에 받기 |
| `data['response']` | 응답 JSON에서 텍스트만 꺼내기 |

---

## 파일 2: `2.qwen_rag.py` — Ollama + RAG (검색 강화 AI)

### RAG란?

> AI가 모르는 내용을 **내가 가진 자료에서 찾아서** 답하게 하는 기술

```
일반 AI:   질문 → AI가 기억으로만 답변 (내 자료 모름)

RAG AI:    질문 → 내 자료에서 관련 내용 검색 → AI에게 같이 전달 → 정확한 답변
```

### 전체 흐름 그림

```
① 자료 준비
   문서들 → OpenAI 임베딩 → 숫자 벡터 → FAISS DB에 저장

② 질문 처리
   사용자 질문 → 숫자 벡터 → FAISS DB에서 유사한 문서 검색
   → 관련 문서 + 질문 → Ollama(로컬 AI) → 최종 답변
```

### 핵심 개념: 임베딩(Embedding)

텍스트를 AI가 비교할 수 있는 **숫자 배열**로 바꾸는 것입니다.

```
"파이썬은 쉽다"  →  [0.12, -0.34, 0.87, ...]  (1536개 숫자)
"Python is easy" →  [0.11, -0.33, 0.85, ...]  (비슷한 숫자!)

→ 의미가 비슷하면 숫자도 비슷해짐
```

### 핵심 개념: FAISS

**숫자 벡터들을 모아두고 빠르게 검색**하는 데이터베이스입니다.

```python
index = faiss.IndexFlatL2(1536)   # 1536차원 벡터 저장소 생성
index.add(doc_embeddings)         # 문서 벡터들 저장

# 질문 벡터와 가장 가까운 문서 1개 찾기
distance, indices = index.search(query_vector, k=1)
```

### 유사도 점수

```python
true_distance = np.sqrt(distance[0][0])
similarity_score = 1 / (1 + true_distance)

# 점수가 높을수록 = 질문과 관련성이 높음
# 0.60 미만이면 = 관련 없다고 판단 → "모른다" 반환
```

| 유사도 점수 | 의미 |
|------------|------|
| 0.9 이상 | 매우 관련 있음 |
| 0.7 ~ 0.9 | 관련 있음 |
| 0.6 ~ 0.7 | 약간 관련 있음 |
| 0.6 미만 | 관련 없음 → 답변 거부 |

### 코드 흐름 요약

```python
# 1단계: 문서를 숫자로 변환 후 저장
documents = ["문서1", "문서2", "문서3"]
for doc in documents:
    vector = get_embedding(doc)    # 텍스트 → 숫자 배열
    index.add(vector)              # FAISS DB에 저장

# 2단계: 질문 처리
def rag_query(user_query):
    query_vector = get_embedding(user_query)        # 질문도 숫자로 변환
    distance, indices = index.search(query_vector)  # 가장 가까운 문서 찾기
    retrieved_doc = documents[indices[0][0]]        # 문서 꺼내기

    if similarity_score < 0.60:
        return "모르겠습니다"                        # 관련 없으면 거부

    prompt = f"[질문] {user_query}\n[자료] {retrieved_doc}"
    return ask_qwen(prompt)                         # Ollama에 질문+자료 전달
```

---

## OpenAI vs Ollama 역할 비교

이 코드에서 두 AI를 **역할 분담**해서 씁니다:

| 역할 | 담당 | 이유 |
|------|------|------|
| 임베딩 (숫자 변환) | OpenAI API | 품질이 높음 (유료) |
| 최종 답변 생성 | Ollama (로컬) | 무료, 개인정보 안전 |

---

## 파일 3: `3.qwen_rag_homework.py` — RAG 챗봇 완성본 (과제)

`2.qwen_rag.py`는 질문이 코드 안에 고정되어 있어서 한 번 실행하면 끝났습니다.  
이 파일은 `1.qwen.py`처럼 **계속 대화할 수 있도록** 완성한 버전입니다.

### 달라진 점

| 항목 | `2.qwen_rag.py` | `3.qwen_rag_homework.py` |
|------|-----------------|--------------------------|
| 질문 방식 | 코드 안에 질문 고정 | 직접 입력 가능 |
| 대화 횟수 | 한 번 실행 후 종료 | `while True`로 계속 대화 |
| 종료 방법 | 없음 | `exit` 입력 |
| 디버그 출력 | 숫자 벡터 등 많이 출력 | 제거 |

### 실행 방법

```bash
python 3.qwen_rag_homework.py
```

```
RAG 챗봇을 시작합니다. 종료하려면 'exit'를 입력하세요.

나: 홍길동은 누구인가요?
응답: 홍길동은 2020년 1월 1일 생으로 ...

나: 오늘 날씨는?
응답: 해당 내용은 적합한 답변을 찾을 수 없습니다.  ← 관련 자료 없으면 거부

나: exit
종료합니다.
```

### 핵심 추가 코드

```python
# 기존: 질문이 코드 안에 고정
query = "저작권협회는 누구인가요?"
print(rag_query(query))

# 완성: while 루프로 계속 대화 가능
while True:
    user_input = input("\n나: ")
    if user_input == "exit":
        print("종료합니다.")
        break
    print("응답:", rag_query(user_input))
```

---

## 전체 실습 요약

```
1.qwen.py              →  Ollama로 간단한 채팅봇 만들기
2.qwen_rag.py          →  RAG 개념 실습 (질문 고정, 한 번만 실행)
3.qwen_rag_homework.py →  RAG 챗봇 완성 (계속 대화 가능한 인터랙티브 버전)
```

### 배운 핵심 기술

- **Ollama**: 로컬에서 무료로 AI 모델 실행
- **HTTP 요청**: Python으로 Ollama API 호출 (`requests.post`)
- **임베딩**: 텍스트를 숫자 벡터로 변환
- **FAISS**: 벡터 유사도 검색 데이터베이스
- **RAG**: 내 문서를 AI 답변에 활용하는 기술
- **while 루프**: 챗봇을 인터랙티브하게 만드는 방법
