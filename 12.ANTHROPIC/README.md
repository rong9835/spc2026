# 12. Anthropic API 핵심 요약

> 🎯 Claude AI를 파이썬에서 직접 사용하는 방법을 배웁니다.

---

## 📁 폴더 구조

```
12.ANTHROPIC/
├── 1.basic/          ← Anthropic SDK 직접 사용
│   ├── 1.intro.py    ← 기본 메시지 보내기
│   ├── 2.chat.py     ← 대화 기록 유지하기
│   ├── 3.models.py   ← 모델별 성능 비교
│   └── 4.thinking.py ← AI 사고 과정 보기
└── 2.langchain/      ← LangChain으로 Claude 사용
    ├── 1.intro.py    ← LangChain 기본 연결
    └── 2.template.py ← 프롬프트 템플릿
```

---

## 🧩 핵심 개념 한눈에 보기

| 개념 | 쉬운 비유 | 역할 |
|------|-----------|------|
| **Anthropic SDK** | 전화기 | Claude AI에 직접 전화 걸기 |
| **LangChain** | 전화 앱 | 전화를 더 편리하게 해주는 앱 |
| **messages** | 대화 기록장 | 이전 대화를 기억하는 메모 |
| **temperature** | 창의성 조절 버튼 | 높을수록 더 창의적인 답변 |
| **streaming** | 실시간 자막 | 답변을 한 글자씩 바로 출력 |
| **thinking** | AI 속마음 | AI가 어떻게 생각하는지 보여줌 |

---

## 📌 1. 기본 메시지 보내기 (`1.basic/1.intro.py`)

### 핵심 코드

```python
import anthropic

client = anthropic.Anthropic()  # Claude에 연결

message = client.messages.create(
    model="claude-haiku-4-5",   # 어떤 모델 사용할지
    max_tokens=300,              # 최대 몇 글자 답할지
    messages=[{
        "role": "user",
        "content": "안녕! 한 문장으로 너를 소개해줘."
    }]
)

print(message.content[0].text)  # 답변 출력
```

### 💡 OpenAI와 비교

| | OpenAI | Anthropic |
|---|--------|-----------|
| 라이브러리 | `openai` | `anthropic` |
| 클라이언트 | `openai.OpenAI()` | `anthropic.Anthropic()` |
| 메시지 생성 | `client.chat.completions` | `client.messages.create` |

---

## 📌 2. 대화 기록 유지하기 (`1.basic/2.chat.py`)

### 핵심 아이디어

> **AI는 기본적으로 기억이 없다!**
> 이전 대화를 직접 `messages` 배열에 쌓아서 보내야 한다.

```python
messages = []  # 대화 기록을 담는 바구니

def ask(question):
    # 1. 내 질문을 바구니에 넣기
    messages.append({'role': 'user', 'content': question})
    
    # 2. 바구니 전체를 AI에게 보내기
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        temperature=1.0,   # 창의성 (0~1, 높을수록 다양한 답변)
        messages=messages  # 이전 대화 모두 포함!
    )
    
    answer = message.content[0].text
    
    # 3. AI 답변도 바구니에 넣기
    messages.append({'role': 'assistant', 'content': answer})
    return answer

ask("내 이름은 홍길동이야")
ask("그래서, 내가 누구라고??")  # 이전 대화를 기억함!
```

### 🗂️ messages 배열 구조

```
[
  {"role": "user",      "content": "내 이름은 홍길동이야"},
  {"role": "assistant", "content": "안녕하세요, 홍길동님!"},
  {"role": "user",      "content": "그래서, 내가 누구라고??"},
  ...
]
```

---

## 📌 3. 모델 비교하기 (`1.basic/3.models.py`)

### Claude 모델 종류

| 모델 | 특징 | 비유 |
|------|------|------|
| **Haiku** | 빠르고 저렴 | 자전거 (가볍고 빠름) |
| **Sonnet** | 균형잡힌 성능 | 자동차 (일반 용도) |
| **Opus** | 강력한 고성능 | 스포츠카 (복잡한 작업) |

### 핵심 코드

```python
import time

models = ['claude-haiku-4-5', 'claude-sonnet-4-6', 'claude-opus-4-8']

for model in models:
    start = time.time()  # 시간 측정 시작
    
    msg = client.messages.create(
        model=model,
        max_tokens=500,
        messages=[{"role": "user", "content": "..."}]
    )
    
    elapsed = time.time() - start  # 걸린 시간
    
    print(f"[{model}] {elapsed:.1f}초, {msg.usage.output_tokens} 토큰")
```

> **토큰(Token)** = AI가 읽고 쓰는 단위. 영어는 단어, 한국어는 글자 단위로 생각하면 됨.

---

## 📌 4. AI 사고 과정 보기 (`1.basic/4.thinking.py`)

### 스트리밍 + Thinking 이란?

```
일반 방식: 답변이 다 만들어진 후 한번에 출력
스트리밍:  한 글자씩 실시간으로 출력 (ChatGPT 처럼)
Thinking:  AI가 답변 전에 "생각하는 과정"도 보여줌
```

### 핵심 코드

```python
with client.messages.stream(
    model='claude-opus-4-8',
    max_tokens=2000,
    thinking={"type": "adaptive", "display": "summarized"},  # 사고 과정 활성화
    messages=[{"role": "user", "content": "12 x 13을 단계별로 설명해줘"}]
) as stream:
    for event in stream:
        if event.type == "content_block_delta":
            if event.delta.type == "thinking_delta":
                print(event.delta.thinking, end="")  # 생각 출력
            elif event.delta.type == "text_delta":
                print(event.delta.text, end="")      # 답변 출력
```

---

## 📌 5. LangChain으로 연결하기 (`2.langchain/1.intro.py`)

### LangChain이란?

> 다양한 AI 모델을 **똑같은 방식**으로 쓸 수 있게 해주는 도구

```python
# OpenAI 사용할 때
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model='gpt-4o')

# Anthropic 사용할 때 (방법이 같음!)
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model='claude-sonnet-4-6')

# 이후 코드는 동일하게 사용
response = llm.invoke('인공지능에 대해서 설명해주세요')
print(response.content)
```

---

## 📌 6. 프롬프트 템플릿 (`2.langchain/2.template.py`)

### 왜 템플릿을 쓸까?

> **재사용** 가능한 질문 틀을 만들어서, 변수만 바꿔 여러 번 사용

### 두 가지 템플릿 종류

#### ① PromptTemplate (단순 텍스트)

```python
from langchain_core.prompts import PromptTemplate

template = PromptTemplate.from_template('다음 주제에 대해 설명하시오: {topic}')

# 변수만 바꿔서 재사용
result1 = llm.invoke(template.format(topic='LLM기술'))
result2 = llm.invoke(template.format(topic='transformer 기술'))
```

#### ② ChatPromptTemplate (역할 지정 대화형)

```python
from langchain_core.prompts import ChatPromptTemplate

chat_template = ChatPromptTemplate.from_messages([
    ('system', '당신은 {role} 전문가입니다.'),   # AI 역할 설정
    ('human', '{concept}에 대해 설명해주세요.'),  # 사용자 질문
])

# 파이프(|)로 연결 → chain 만들기
chain = chat_template | llm

result = chain.invoke({
    'role': '인공지능',
    'concept': '트랜스포머'
})
```

### 🔗 Chain이란?

```
프롬프트 → AI → 결과
  (템플릿) | (LLM) = chain
```

> 레고 블록처럼 여러 단계를 `|` 기호로 연결하는 방식

---

## 🔑 전체 흐름 요약

```
1. API 키 설정 (.env 파일)
        ↓
2. 클라이언트 생성 (Anthropic() 또는 ChatAnthropic())
        ↓
3. 메시지 전송 (messages 배열로 대화 기록 관리)
        ↓
4. 응답 출력 (message.content[0].text)
```

---

## ⚙️ 환경 설정

```bash
# 필수 패키지 설치
pip install anthropic
pip install langchain-anthropic
pip install python-dotenv

# .env 파일에 API 키 저장
ANTHROPIC_API_KEY=sk-ant-xxxxxxxx
```

```python
# 코드에서 불러오기
from dotenv import load_dotenv
load_dotenv()  # .env 파일 자동으로 읽어옴
```

---

## 📝 자주 헷갈리는 것

| 헷갈리는 것 | 정답 |
|------------|------|
| `message.content` 왜 `[0]`? | AI 답변이 리스트로 오기 때문 (보통 첫 번째 요소 사용) |
| `temperature`는 뭐? | 0에 가까울수록 일관된 답변, 1에 가까울수록 다양한 답변 |
| `max_tokens`는 왜 설정? | 너무 긴 답변 방지 (비용 절감) |
| `streaming`이 왜 필요? | 긴 답변도 기다리지 않고 바로바로 보여주기 위해 |
