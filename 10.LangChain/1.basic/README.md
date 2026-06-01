# LangChain 기초 핵심 요약

> 파이썬으로 AI(ChatGPT)를 내 프로그램에 연결하는 방법을 배웁니다.

---

## LangChain이 뭔가요?

**LangChain** = AI 모델(ChatGPT 등)을 파이썬 코드에서 쉽게 쓸 수 있게 도와주는 도구

> 비유: ChatGPT 웹사이트에서 직접 타이핑하는 대신, **파이썬 코드가 자동으로 ChatGPT에게 질문하고 답을 받아오는 것**

---

## 사전 준비

```bash
pip install langchain langchain-openai flask python-dotenv
```

`.env` 파일에 API 키 저장:
```
OPENAI_API_KEY=sk-여기에본인키입력
```

---

## 1단계: 가장 기본 — AI에게 질문하기 (`1.intro.py`)

```python
from langchain_openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # .env 파일에서 API 키 불러오기

llm = OpenAI(model="gpt-4o-mini")  # AI 모델 준비

result = llm.invoke("오늘 저녁은 무엇을 먹을까요?")  # 질문 보내기
print(result)  # 답변 출력
```

**핵심 흐름:**
```
내 코드 → llm.invoke("질문") → ChatGPT → 답변 → print()
```

---

## 2단계: 두 가지 모델 종류 (`2.chat.py`)

| 구분 | 클래스 | 모델 예시 | 용도 |
|------|--------|-----------|------|
| **단발성 질문** | `OpenAI` | `gpt-3.5-turbo-instruct` | 번역, 간단한 명령 |
| **대화형 질문** | `ChatOpenAI` | `gpt-4o-mini` | Q&A, 채팅 |

### 메시지 3총사

```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
```

| 메시지 | 역할 | 비유 |
|--------|------|------|
| `SystemMessage` | AI의 역할/성격 설정 | "너는 요리사야" |
| `HumanMessage` | 내가 하는 말 | 사람의 질문 |
| `AIMessage` | AI가 한 말 (이전 대화) | AI의 이전 답변 |

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

llm = ChatOpenAI(model='gpt-4o-mini')

prompt = [
    SystemMessage(content="당신은 창의력이 높은 작명가입니다."),  # 역할 설정
    HumanMessage(content="게임 회사 이름 3개 지어주세요"),         # 내 질문
]

result = llm.invoke(prompt)
print(result.content)  # ← .content로 텍스트만 꺼내기
```

---

## 3단계: 대화 이어가기 (`3.chat2.py`)

`AIMessage`를 넣으면 **이전 대화 내용을 기억**한 것처럼 동작합니다.

```python
prompt = [
    SystemMessage(content="당신은 경력 10년차 호텔 쉐프입니다."),
    HumanMessage(content="오늘 저녁 메뉴를 추천해줘."),
    AIMessage(content="비빔밥은 어떠신가요?"),     # ← AI가 이렇게 말했다고 알려줌
    HumanMessage(content="아~ 좋아. 재료는?"),      # ← 이어서 질문
]

result = llm.invoke(prompt)
print(result.content)
```

> 비유: 대화 내용을 **메모지에 적어서 AI에게 보여주는 것** — AI는 원래 이전 대화를 기억 못하지만, 우리가 직접 넘겨주면 기억하는 척 할 수 있음

---

## 4단계: API 서버 만들기 (`4.flask_api.py`)

Flask로 LangChain을 **웹 API**로 만들면, 다른 앱에서도 AI를 쓸 수 있어요.

```python
from flask import Flask, request, jsonify
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

app = Flask(__name__)
llm = ChatOpenAI(model='gpt-4o-mini')

# GET 요청: /api/dinner 접속하면 AI가 저녁 메뉴 추천
@app.route('/api/dinner')
def dinner():
    prompt = [
        SystemMessage(content="당신은 경력 10년차 호텔 쉐프입니다."),
        HumanMessage(content="오늘 저녁 메뉴를 추천해줘."),
    ]
    result = llm.invoke(prompt)
    return jsonify({"result": "success", "chatbot": result.content})

# POST 요청: 사용자가 보낸 데이터로 동적으로 질문
@app.route('/api/name', methods=['POST'])
def name():
    data = request.get_json()           # 사용자가 보낸 JSON 받기
    product = data.get("product")       # product 값 꺼내기
    
    prompt = [
        SystemMessage(content="You are a creative branding expert."),
        HumanMessage(content=f"{product}를 만드는 회사 이름을 추천해줘"),
    ]
    result = llm.invoke(prompt)
    return jsonify({"result": "success", "chatbot": result.content})

if __name__ == "__main__":
    app.run(debug=True)
```

**API 흐름:**
```
브라우저/앱 → HTTP 요청 → Flask → LangChain → ChatGPT → JSON 응답
```

---

## 5단계: 웹 페이지까지 연결하기 (`5.flask_web.py` + `index.html`)

Flask가 HTML 파일도 서빙해서 **완성된 웹앱**을 만들어요.

```python
# Flask에서 HTML 파일 제공
@app.route("/")
def index():
    return send_from_directory("static", "index.html")
```

```
프로젝트 구조:
├── 5.flask_web.py       # 서버 (백엔드)
└── static/
    └── index.html       # 화면 (프론트엔드)
```

**HTML에서 AI 호출하는 핵심 코드:**
```javascript
// 버튼 클릭 시
const response = await fetch('/api/name', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({product: userInput})  // 서버로 전송
});

const data = await response.json();  // AI 응답 받기
// 화면에 결과 출력...
```

---

## 전체 흐름 한눈에 보기

```
[사용자] 입력
    ↓
[HTML/JS] fetch()로 백엔드에 POST 요청
    ↓
[Flask] 요청 받아서 LangChain에 전달
    ↓
[LangChain] 메시지 조립 후 ChatGPT 호출
    ↓
[ChatGPT] 답변 생성
    ↓
[Flask] JSON으로 응답
    ↓
[HTML/JS] 화면에 결과 표시
```

---

## 핵심 용어 정리

| 용어 | 설명 |
|------|------|
| `llm.invoke()` | AI에게 질문을 보내고 답변을 받는 함수 |
| `result.content` | AI 답변에서 텍스트만 꺼내는 방법 |
| `SystemMessage` | AI의 역할/성격을 설정하는 메시지 |
| `HumanMessage` | 사람이 하는 말 |
| `AIMessage` | AI가 했던 말 (대화 이어가기용) |
| `jsonify()` | 파이썬 딕셔너리를 JSON으로 변환 |
| `load_dotenv()` | `.env` 파일에서 환경변수 불러오기 |

---

## 실습 순서 추천

```
1.intro.py  →  2.chat.py  →  3.chat2.py  →  4.flask_api.py  →  5.flask_web.py
   AI 기초       모델 차이     대화 이어가기    API 서버 만들기     웹앱 완성
```
