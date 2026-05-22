# OpenAI API 핵심 정리

> 파이썬 초보자를 위한 쉬운 설명

---

## 목차

1. [OpenAI API란?](#1-openai-api란)
2. [준비하기 - API 키와 환경변수](#2-준비하기---api-키와-환경변수)
3. [REST API로 직접 호출하기](#3-rest-api로-직접-호출하기)
4. [SDK로 더 쉽게 호출하기](#4-sdk로-더-쉽게-호출하기)
5. [역할(role) 이해하기](#5-역할role-이해하기)
6. [대화 히스토리 - 기억하는 챗봇](#6-대화-히스토리---기억하는-챗봇)
7. [스마트 히스토리 - 요약으로 메모리 절약](#7-스마트-히스토리---요약으로-메모리-절약)
8. [Vision - 이미지 분석하기](#8-vision---이미지-분석하기)
9. [주요 파라미터 정리](#9-주요-파라미터-정리)
10. [핵심 개념 한눈에 보기](#10-핵심-개념-한눈에-보기)

---

## 1. OpenAI API란?

### 비유로 이해하기

> **API = 식당 주문서**
>
> - 내가 직접 요리하지 않아도 됨
> - 주문서(요청)를 작성해서 보내면
> - 식당(OpenAI 서버)이 음식(AI 답변)을 만들어서 돌려줌

```
내 코드  →  요청(질문)  →  OpenAI 서버
내 코드  ←  응답(답변)  ←  OpenAI 서버
```

### 핵심 엔드포인트

```
https://api.openai.com/v1/chat/completions
```

- `completions` = "이어서 완성해줘"라는 뜻
- 내 메시지를 보내면 → AI가 이어서 답변을 완성해줌

---

## 2. 준비하기 - API 키와 환경변수

### API 키란?

> **API 키 = 출입증**
>
> OpenAI 서비스를 사용하려면 신분증(API 키)이 필요함

### .env 파일로 안전하게 관리

```
# .env 파일 (절대 GitHub에 올리면 안 됨!)
OPENAI_API_KEY=sk-proj-xxxxx...
```

### 파이썬에서 불러오기

```python
from dotenv import load_dotenv
import os

load_dotenv()  # .env 파일 읽기

api_key = os.getenv('OPENAI_API_KEY')  # 환경변수에서 키 가져오기
```

> **왜 환경변수를 쓰나요?**
> API 키를 코드에 직접 쓰면 → 코드를 공유할 때 키가 유출됨
> 환경변수에 넣으면 → 키는 숨기고 코드만 공유 가능

---

## 3. REST API로 직접 호출하기

### 파일: `1.restapi/1.restapi.py`

```python
import requests

response = requests.post(
    'https://api.openai.com/v1/chat/completions',  # 주소
    json={                                          # 보낼 데이터 (주문서)
        'model': 'gpt-3.5-turbo',
        'messages': [
            {'role': 'system', 'content': '너는 작명가야.'},
            {'role': 'user', 'content': '강아지 이름 추천해줘'}
        ],
        'temperature': 1.0,
    },
    headers={                                       # 인증 정보
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
)

data = response.json()
answer = data['choices'][0]['message']['content']  # 답변 꺼내기
```

### 응답 구조 이해하기

```
data
└── choices
    └── [0]                 ← 첫 번째 답변 (보통 하나만 옴)
        └── message
            └── content     ← 실제 AI 답변 텍스트
```

### REST API vs SDK 비교

| 구분 | REST API | SDK |
|------|----------|-----|
| 방법 | `requests.post()` 직접 호출 | `openai` 라이브러리 사용 |
| 코드량 | 많음 (헤더, URL 직접 작성) | 적음 (라이브러리가 처리) |
| 배우는 이유 | API 동작 원리 이해 | 실무에서 주로 사용 |

---

## 4. SDK로 더 쉽게 호출하기

### 설치

```bash
pip install openai   # 최신 버전 (4.x)
```

### 구버전 vs 신버전 비교

**구버전 (0.28 - 옛날 방식)**
```python
import openai
openai.api_key = '키'                       # 전역 설정

response = openai.ChatCompletion.create(    # 함수 이름이 길고 복잡
    model='gpt-3.5-turbo',
    messages=[...]
)
```

**신버전 (4.x - 현재 방식)** ✅
```python
import openai
client = openai.OpenAI(api_key='키')        # 클라이언트 객체 생성

response = client.chat.completions.create( # client.으로 시작
    model='gpt-3.5-turbo',
    messages=[...]
)
```

> **왜 바뀌었나요?**
> 클라이언트 방식이 더 안전하고, 여러 API 키를 동시에 쓸 수 있어서 업그레이드됨

---

## 5. 역할(role) 이해하기

ChatGPT와 대화할 때 3가지 역할이 있음:

| role | 누구? | 역할 |
|------|-------|------|
| `system` | 🎭 감독 | AI의 성격/역할 설정 ("너는 작명가야") |
| `user` | 🙋 사용자 | 내가 보내는 질문 |
| `assistant` | 🤖 AI | AI가 답변한 내용 |

### 예시

```python
messages = [
    {'role': 'system',    'content': '너는 친절한 요리사야.'},   # AI 역할 설정
    {'role': 'user',      'content': '파스타 만드는 법 알려줘'}, # 내 질문
    {'role': 'assistant', 'content': '파스타는...'},             # AI 이전 답변
    {'role': 'user',      'content': '더 자세히 알려줘'},        # 후속 질문
]
```

> **system 프롬프트는 첫 번째에 한 번만!**
> 대화가 길어져도 system은 항상 `messages[0]`에 고정

---

## 6. 대화 히스토리 - 기억하는 챗봇

### 파일: `1.restapi/3.restapi_chat_history.py`

### 문제: AI는 기억이 없다

```
나: "내 이름은 김철수야"
AI: "반가워요, 김철수님!"

나: "내 이름이 뭐야?"
AI: "저는 당신의 이름을 모릅니다." ← 기억 못 함!
```

### 해결: messages 리스트에 쌓기

```python
messages = [
    {'role': 'system', 'content': '너는 친절한 챗봇이야.'}
]

# 1번째 대화
messages.append({'role': 'user', 'content': '내 이름은 김철수야'})
response = API_호출(messages)
messages.append({'role': 'assistant', 'content': response})

# 2번째 대화 (이전 대화가 다 담겨있음)
messages.append({'role': 'user', 'content': '내 이름이 뭐야?'})
response = API_호출(messages)  # AI가 위 대화 기록을 보고 답변
```

### 히스토리 개수 제한

```python
# 메모리 절약: 최근 10개만 유지
messages = [messages[0]] + messages[-10:]
#           ^^^^^^^^^^^     ^^^^^^^^^^^^
#           system 유지     최근 10개만
```

> **왜 제한하나요?**
> 대화가 너무 길면 → API 비용 증가, 속도 느려짐
> 일반적으로 최근 10~20개면 충분

---

## 7. 스마트 히스토리 - 요약으로 메모리 절약

### 파일: `1.restapi/4.restapi_chat_smart_history.py`

### 단순 삭제 vs 스마트 요약

```
단순 삭제: 오래된 대화 → 그냥 버림 (중요한 내용도 날아감)
스마트 요약: 오래된 대화 → AI가 요약해서 보관
```

### 동작 방식

```
[처음]
messages = [system, user1, ai1, user2, ai2, user3, ai3 ...]

[대화가 10개 넘으면]
오래된 대화들을 AI에게 요약 요청 →
"[대화 요약]: 사용자가 강아지 이름을 물었고, AI는 뭉치, 초코 등을 추천했음"

[새 messages 구조]
messages = [
    system,        ← 원래 역할 설정
    요약_메시지,    ← 오래된 대화 요약본
    최근_대화들    ← 최근 10개 유지
]
```

### 핵심 코드

```python
def summarize_conversation(conversation_list):
    summary_prompt = [
        {'role': 'system', 'content': '너는 대화 요약 전문가야. 핵심만 간결하게 요약해줘.'},
        {'role': 'user', 'content': str(conversation_list)}
    ]
    return call_chatgpt(summary_prompt, temperature=0.3)  # temperature 낮게 = 일관된 요약
```

> **temperature=0.3인 이유?**
> 요약은 창의적일 필요가 없음 → 낮을수록 정확하고 일관된 답변

---

## 8. Vision - 이미지 분석하기

### 파일: `2.sdk/4.vision.py`

### 이미지를 텍스트로 변환하는 과정 (Base64)

```
이미지 파일 (0,1로 된 바이너리)
    ↓
base64 인코딩 (텍스트 문자열로 변환)
    ↓
API로 전송 (텍스트만 보낼 수 있어서 변환 필요)
```

```python
import base64

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as file:           # rb = 바이너리로 읽기
        return base64.b64encode(file.read()).decode('utf-8')
```

### Vision API 호출

```python
response = client.chat.completions.create(
    model='gpt-4.1-mini',   # ← 중요! gpt-4 계열만 이미지 지원
    messages=[{
        'role': 'user',
        'content': [
            {'type': 'text', 'text': '이 이미지에 뭐가 있나요?'},
            {'type': 'image_url', 'image_url': {'url': image_base64}}
        ]
    }]
)
```

### 텍스트 vs 이미지 메시지 구조 비교

```python
# 텍스트만 (일반)
{'role': 'user', 'content': '안녕하세요'}

# 이미지 포함 (Vision)
{'role': 'user', 'content': [
    {'type': 'text',      'text': '질문 내용'},
    {'type': 'image_url', 'image_url': {'url': 이미지_base64}}
]}
```

> **gpt-3.5-turbo는 이미지를 못 봄!**
> Vision 기능 = gpt-4.1-mini, gpt-4o, gpt-4-turbo 등 gpt-4 계열만 가능

---

## 9. 주요 파라미터 정리

### model - 어떤 AI를 쓸지

| 모델 | 특징 | 비용 |
|------|------|------|
| `gpt-3.5-turbo` | 빠르고 저렴, 텍스트만 | 저렴 |
| `gpt-4.1-mini` | 이미지 가능, 균형 잡힘 | 보통 |
| `gpt-4o` | 가장 강력, 멀티모달 | 비쌈 |

### temperature - 창의성 조절

```
0.0  ─────────────────────────  2.0
일관적                          창의적
(요약, 번역)              (글쓰기, 아이디어)
```

| 값 | 언제 쓰나 |
|----|----------|
| `0.0 ~ 0.3` | 요약, 번역, 코드 생성 (정확성 중요) |
| `0.7 ~ 1.0` | 일반 대화, 창의적 글쓰기 |
| `1.5 ~ 2.0` | 매우 창의적인 작업 (불안정할 수 있음) |

### top_p - 다양성 조절

```python
'top_p': 0.5   # 확률 상위 50% 단어만 선택 (더 일관적)
'top_p': 1.0   # 모든 단어 고려 (더 다양함)
```

> **temperature와 top_p 중 하나만 조정하는 것을 권장**

---

## 10. 핵심 개념 한눈에 보기

### 학습 흐름 요약

```
1단계: REST API
  requests.post() → OpenAI 서버에 직접 HTTP 요청
  (API 동작 원리 이해)
       ↓
2단계: SDK
  openai 라이브러리 → 더 간단하고 편리하게
  (실무 코드 작성)
       ↓
3단계: 대화 히스토리
  messages 리스트에 누적 → 문맥 기억하는 챗봇
  (기본 챗봇 구현)
       ↓
4단계: 스마트 히스토리
  오래된 대화 요약 저장 → 비용 절약 + 맥락 유지
  (실용적인 챗봇 구현)
       ↓
5단계: Vision
  base64 이미지 → gpt-4 계열로 이미지 분석
  (멀티모달 AI 활용)
```

### 자주 쓰는 코드 패턴

```python
# ✅ 기본 세팅 (항상 이렇게 시작)
from dotenv import load_dotenv
import os
import openai

load_dotenv()
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# ✅ 기본 API 호출
response = client.chat.completions.create(
    model='gpt-3.5-turbo',
    messages=[
        {'role': 'system', 'content': 'AI 역할 설정'},
        {'role': 'user',   'content': '질문 내용'}
    ]
)
answer = response.choices[0].message.content

# ✅ 답변 꺼내기 (항상 이 경로)
answer = response.choices[0].message.content
```

### 오류 처리 기본

```python
try:
    response = client.chat.completions.create(...)
    return response.choices[0].message.content
except Exception as e:
    print(f'오류 발생: {e}')
    return '오류가 발생했습니다.'
```

---

## 체크리스트

처음 OpenAI API를 쓸 때 확인할 것들:

- [ ] `.env` 파일에 `OPENAI_API_KEY` 저장했나?
- [ ] `.gitignore`에 `.env` 추가했나? (키 유출 방지)
- [ ] `pip install openai python-dotenv` 설치했나?
- [ ] `load_dotenv()` 호출했나?
- [ ] Vision 기능은 gpt-4 계열 모델 사용했나?
- [ ] 답변은 `response.choices[0].message.content`로 꺼내나?

---

*파이썬 초보자를 위한 OpenAI API 핵심 정리 | 2026*
