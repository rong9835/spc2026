# 영어 교육 사이트 - 핵심 요약 정리

> ChatGPT API를 활용해 초등학생 학년별 영어 대화 학습을 제공하는 웹 앱

---

## 📌 이 프로젝트가 하는 일

```
사용자가 학년 선택 → 커리큘럼 선택 → ChatGPT 선생님과 영어 대화
```

---

## 🗂️ 파일 구조

```
1.english_edu/
├── app.py                    ← 서버 (백엔드 전체 담당)
└── templates/
    ├── base.html             ← 공통 레이아웃 (모든 페이지의 틀)
    ├── home.html             ← 홈 화면
    ├── grade.html            ← 학년별 커리큘럼 목록 화면
    └── curriculum.html       ← 실제 채팅 화면
```

---

## 🔑 핵심 개념 1 - Flask 라우트(Route)

> **비유**: 라우트는 "URL 주소에 따라 어떤 방을 열어줄지" 정하는 안내판

```python
@app.route('/')           # 주소: localhost:5000/
def home():               # 홈 화면 보여줘

@app.route('/grade/<int:grade>')       # 주소: /grade/3
def grade(grade):                      # 3학년 커리큘럼 보여줘

@app.route('/grade/<int:grade>/curriculum/<int:curriculum_id>')
def curriculum(grade, curriculum_id):  # 채팅 화면 보여줘
```

| URL 패턴 | 하는 일 |
|----------|---------|
| `/` | 홈 화면 |
| `/grade/3` | 3학년 커리큘럼 목록 |
| `/grade/3/curriculum/0` | 3학년 첫 번째 커리큘럼 채팅 |
| `/chat/stream` (POST) | SSE 스트리밍 채팅 응답 |

---

## 🔑 핵심 개념 2 - 커리큘럼 데이터 구조

> **비유**: 파이썬 딕셔너리는 "사물함"과 같아요. 번호(key)로 내용물(value)을 꺼냄

```python
curriculums = {
    1: ['기초 인사', '간단한 문장', '동물이름'],   # 1학년 → 3개 주제
    2: ['학교 생활', '가족 소개', '자기 소개'],
    3: ['취미와 운동', '날씨 묘사', '간단한 이야기'],
    # ...6학년까지
}
```

- **key** (번호): 학년 (1~6)
- **value** (내용): 그 학년의 커리큘럼 목록

---

## 🔑 핵심 개념 3 - SSE (Server-Sent Events) 스트리밍

> **비유**: 일반 채팅은 "편지"처럼 다 써서 보내지만, SSE는 "전화"처럼 실시간으로 글자가 흘러옴

### 일반 방식 vs SSE 방식

```
일반 방식: [사용자 질문] → [서버가 다 생각] → [한 번에 전송]
SSE 방식:  [사용자 질문] → [서버가 조금씩 생각하면서] → [글자 단위로 실시간 전송]
```

### 서버 코드 (app.py)

```python
@app.route('/chat/stream', methods=['POST'])
def chat_stream():
    # 1. 프론트에서 받은 데이터 꺼내기
    grade = data['grade']
    curriculum_title = data['curriculumTitle']
    user_input = data['input']

    def generate_response():          # 발전기(generator) 함수
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {
                    'role': 'system',                         # AI에게 역할 부여
                    'content': f'너는 {grade}학년 학생에게 {curriculum_title} 주제로 영어를 가르치는 선생님이야'
                },
                {'role': 'user', 'content': user_input}      # 학생 질문
            ],
            stream=True,              # 스트리밍 ON
        )
        for chunk in response:        # 조각(chunk)이 올 때마다
            content = chunk.choices[0].delta.content
            if content:
                yield f'data: {json.dumps({"content": content})}\n\n'  # 조각 전송
        yield 'data: [DONE]\n\n'      # 끝 신호

    return Response(generate_response(), mimetype='text/event-stream')
```

### 프론트 코드 (curriculum.html)

```javascript
// SSE 응답을 조각(chunk)별로 읽어서 화면에 붙이기
const reader = response.body.getReader();   // 스트림 읽기 도구
let fullText = '';

while (true) {
    const { done, value } = await reader.read();  // 조각 하나씩 읽기
    if (done) break;                              // 끝나면 멈춤

    // 'data: {...}' 형태의 줄만 골라내기
    if (line.startsWith('data: ')) {
        const data = line.slice(6);               // 'data: ' 제거
        const parsed = JSON.parse(data);
        fullText += parsed.content;               // 텍스트 누적
        document.getElementById('chat').innerHTML = fullText;  // 화면 갱신
    }
}
```

---

## 🔑 핵심 개념 4 - Jinja2 템플릿 (HTML에서 파이썬 변수 사용)

> **비유**: HTML 안에 `{{ }}` 나 `{% %}` 를 쓰면 파이썬 코드를 HTML에 끼워 넣을 수 있어요

| 문법 | 용도 | 예시 |
|------|------|------|
| `{{ 변수 }}` | 변수 값 출력 | `{{ grade }}` → `3` |
| `{% for %}` | 반복문 | 학년 목록 반복 출력 |
| `{% extends %}` | 다른 템플릿 상속 | `base.html` 틀 가져오기 |
| `{% block %}` | 상속받은 곳에 내용 채우기 | `{% block content %}` |

### 템플릿 상속 흐름

```
base.html (공통 틀: 헤더, 네비, 푸터)
    ↓ extends
home.html / grade.html / curriculum.html (각 페이지 고유 내용만 작성)
```

---

## 🔑 핵심 개념 5 - System Prompt로 AI 역할 설정

> AI에게 "너는 ~야" 라고 역할을 지정하면 그 역할에 맞게 대답해요

```python
messages=[
    {
        'role': 'system',    # ← AI의 정체성/규칙 설정 (사용자에게 안 보임)
        'content': f'너는 초등학교 {grade}학년 학생에게 {curriculum_title} 주제로 영어를 가르치는 선생님이야. 학생이 영어로 대화하게끔 유도해'
    },
    {
        'role': 'user',      # ← 실제 사용자 메시지
        'content': user_input
    }
]
```

| role | 역할 |
|------|------|
| `system` | AI의 성격/규칙 정의 |
| `user` | 사용자 입력 |
| `assistant` | AI의 이전 답변 (메모리 구현 시 사용) |

---

## 🔄 전체 요청 흐름 (데이터 흐름)

```
[사용자] 텍스트 입력 + 전송 버튼 클릭
    ↓
[curriculum.html] fetch('/chat/stream', POST) 요청 전송
    ↓
[app.py] /chat/stream 라우트 실행
    ↓
[OpenAI API] gpt-4o-mini 모델 호출 (stream=True)
    ↓
[app.py] 응답 조각을 SSE 형식으로 yield
    ↓
[curriculum.html] reader.read()로 조각 수신 → 화면에 실시간 출력
```

---

## 💡 추가로 알아두면 좋은 것

### `enumerate()` - 인덱스 번호 붙이기

```python
curriculums_index = list(enumerate(curriculums[grade]))
# [('기초 인사', 0), ('간단한 문장', 1), ('동물이름', 2)]
# → URL에서 curriculum_id=0, 1, 2 로 사용
```

### `url_for()` - URL 자동 생성

```html
<!-- 직접 쓰는 방법 (나쁨) -->
<a href="/grade/3">3학년</a>

<!-- url_for 사용 (좋음) - 함수명으로 URL 자동 생성 -->
<a href="{{ url_for('grade', grade=grade) }}">3학년</a>
```

### `json.dumps()` - 파이썬 딕셔너리 → JSON 문자열

```python
{"content": "Hello"} → '{"content": "Hello"}'   # SSE 전송용
```

---

## ✅ 핵심 요약 한 줄 정리

| 기술 | 한 줄 설명 |
|------|------------|
| **Flask 라우트** | URL마다 실행할 함수를 연결 |
| **딕셔너리** | 키(학년)로 값(커리큘럼 목록)을 꺼내는 자료구조 |
| **SSE 스트리밍** | AI 응답을 글자 단위로 실시간 전송 |
| **Jinja2 템플릿** | HTML 안에서 파이썬 변수/반복문 사용 |
| **System Prompt** | AI에게 역할(선생님)을 부여하는 설정 메시지 |
| **stream=True** | OpenAI가 응답을 한 번에 안 보내고 조각으로 보냄 |
