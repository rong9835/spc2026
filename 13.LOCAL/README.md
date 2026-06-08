# 13. 로컬 LLM (Local LLM) 핵심 요약

> **로컬 LLM이란?**
> ChatGPT처럼 인터넷 서버에 요청하지 않고, **내 컴퓨터에서 직접 AI를 실행**하는 방식입니다.
> 비용이 없고, 인터넷 없이도 동작하며, 개인정보가 외부로 나가지 않습니다.

---

## 핵심 개념 한눈에 보기

```
[Ollama] : AI 모델을 내 컴퓨터에서 실행해주는 프로그램
    └─ mistral, exaone3.5 등 다양한 모델 사용 가능

[LangChain + Ollama] : LangChain으로 Ollama를 더 편리하게 사용
    └─ 프롬프트 → AI → 결과 파싱을 체인으로 연결

[외부 Ollama 서버] : 다른 컴퓨터(서버)의 Ollama에 네트워크로 요청
    └─ HTTP API 방식으로 원격 모델 호출
```

---

## 파일별 설명

### 📄 1.intro.py — Ollama 기초 사용법

```python
import ollama

ollama.pull("mistral")           # 모델 다운로드 (처음 한 번만)
response = ollama.chat(model="mistral", messages=[
    {"role": "user", "content": "인공지능에 대해서 설명해줘"}
])
print(response["message"]["content"])
```

**비유:** Ollama는 "AI 실행기"입니다.
`pull`은 앱 설치, `chat`은 앱 실행이라고 생각하면 됩니다.

| 코드 | 역할 |
|------|------|
| `ollama.pull("mistral")` | AI 모델을 내 PC에 다운로드 |
| `ollama.chat(...)` | 모델에게 질문하고 답변 받기 |
| `messages` 리스트 | 대화 내용 (role: user/assistant) |

> 설치: `pip install ollama`

---

### 📄 2.langchain.py — LangChain으로 Ollama 사용

```python
from langchain_ollama import ChatOllama

llm = ChatOllama(model="mistral")
resp = llm.invoke("안녕? 한마디로 너를 소개해줘")
print(resp.content)
```

**비유:** LangChain은 "AI와 소통하는 표준 리모컨"입니다.
Ollama, OpenAI, Claude 등 어떤 AI든 같은 방식으로 사용할 수 있습니다.

| 코드 | 역할 |
|------|------|
| `ChatOllama(model="mistral")` | 로컬 AI 모델 준비 |
| `llm.invoke("질문")` | 질문하고 답변 받기 |
| `resp.content` | 답변 텍스트 추출 |

> 설치: `pip install langchain-ollama`

---

### 📄 3.langchain2.py — 프롬프트 템플릿 + 체인

```python
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOllama(model="mistral")

prompt = PromptTemplate.from_template(
    "다음 주제로 블로그 개요를 5가지 만들어줘.\n\n주제: {topic}"
)

chain = prompt | llm | StrOutputParser()

print(chain.invoke({"topic": "로컬 LLM 모델 활용"}))
```

**비유:** 체인(`|`)은 "컨베이어 벨트"입니다.
`프롬프트 → AI → 파싱` 순서로 자동으로 처리됩니다.

```
{topic} 변수 채우기  →  AI에게 전달  →  텍스트만 추출
   PromptTemplate    →   ChatOllama  →  StrOutputParser
```

| 구성요소 | 역할 |
|---------|------|
| `PromptTemplate` | `{topic}` 같은 변수를 포함한 프롬프트 틀 |
| `ChatOllama` | 로컬 AI 모델 |
| `StrOutputParser` | AI 응답에서 텍스트만 깔끔하게 추출 |
| `chain.invoke({"topic": "..."})` | 변수 값을 넣어 체인 실행 |

---

### 📄 4.langchain3_stream.py — 스트리밍 (실시간 출력)

```python
chain = prompt | llm | StrOutputParser()

for chunk in chain.stream({"topic": "로컬 LLM 모델 활용"}):
    print(chunk, end="", flush=True)
```

**비유:** `invoke`는 답변이 완성될 때까지 기다렸다가 한 번에 출력,
`stream`은 ChatGPT처럼 **글자가 나오는 대로 실시간으로 출력**합니다.

| 방식 | 특징 |
|------|------|
| `chain.invoke()` | 답변 완성 후 한 번에 출력 (기다림) |
| `chain.stream()` | 답변 생성 중 실시간 출력 (자연스러움) |

> `end="", flush=True` : 줄바꿈 없이 이어서 즉시 출력하는 옵션

---

### 📄 5.external.py — 외부 Ollama 서버에 요청

```python
import requests

OLLAMA_HOST = "http://192.168.0.153:11434"
OLLAMA_ENDPOINT = f"{OLLAMA_HOST}/api/generate"

payload = {
    "model": "exaone3.5",
    "prompt": "파이썬으로 헬로우 월드 코드를 보여줘.",
    "stream": False
}

response = requests.post(OLLAMA_ENDPOINT, json=payload)
data = response.json()
print("모델 응답: ", data.get('response'))
```

**비유:** 내 컴퓨터 대신 **같은 네트워크의 다른 컴퓨터(서버)에 있는 Ollama**를 사용하는 방식입니다.
마치 카페 주문처럼, 내가 요청하면 서버가 AI 응답을 만들어 보내줍니다.

```
내 코드 → HTTP 요청 → [192.168.0.153 서버의 Ollama] → AI 응답 반환
```

| 항목 | 설명 |
|------|------|
| `OLLAMA_HOST` | Ollama가 실행 중인 서버의 IP:포트 |
| `/api/generate` | Ollama의 REST API 엔드포인트 |
| `stream: False` | 스트리밍 없이 완성된 응답을 한 번에 받기 |

---

## 전체 흐름 비교

| 파일 | 방식 | 특징 |
|------|------|------|
| `1.intro.py` | `ollama` 라이브러리 직접 사용 | 가장 단순한 기본 방법 |
| `2.langchain.py` | `LangChain + Ollama` | LangChain 표준 방식 |
| `3.langchain2.py` | `프롬프트 템플릿 + 체인` | 변수 활용, 구조화된 방식 |
| `4.langchain3_stream.py` | `체인 + 스트리밍` | 실시간 출력 |
| `5.external.py` | `HTTP API 직접 호출` | 원격 서버 Ollama 사용 |

---

## 설치 명령어 정리

```bash
# Ollama 설치 (공식 사이트에서 다운로드)
# https://ollama.com

# Python 패키지 설치
pip install ollama
pip install langchain-ollama
pip install requests  # 파이썬 기본 포함, 보통 불필요

# Ollama 모델 다운로드 (터미널에서)
ollama pull mistral
ollama pull exaone3.5
```

---

## 핵심 포인트 3가지

> 1. **Ollama = 내 PC에서 AI 실행** → 무료, 오프라인, 프라이버시 보호
> 2. **LangChain = AI 연결 표준화** → 어떤 AI든 같은 코드로 사용 가능
> 3. **stream vs invoke** → 실시간 출력 필요하면 `stream`, 아니면 `invoke`
