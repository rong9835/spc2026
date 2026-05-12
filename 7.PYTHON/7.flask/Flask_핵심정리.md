# Flask 핵심 정리

## 목차
1. [Flask란?](#1-flask란)
2. [기본 설정 및 앱 실행](#2-기본-설정-및-앱-실행)
3. [라우팅 (Routing)](#3-라우팅-routing)
4. [동적 URL (변수 라우팅)](#4-동적-url-변수-라우팅)
5. [JSON 응답](#5-json-응답)
6. [전체 흐름 요약](#6-전체-흐름-요약)

---

## 1. Flask란?

> **Flask** = 파이썬으로 웹 서버(백엔드)를 만드는 경량 웹 프레임워크

- 브라우저가 요청(Request)을 보내면, Flask가 받아서 응답(Response)을 돌려줌
- 설치: `pip install flask`

```
브라우저 --[요청]--> Flask 서버 --[응답]--> 브라우저
(http://localhost:5000)
```

---

## 2. 기본 설정 및 앱 실행

```python
from flask import Flask

app = Flask(__name__)       # Flask 앱 생성

@app.route('/')             # '/' 주소로 접속하면 아래 함수 실행
def home():
    return "<h1>Hello Flask!</h1>"   # HTML 반환 가능

if __name__ == '__main__':
    app.run(debug=True)     # 서버 실행
```

### 핵심 포인트

| 코드 | 의미 |
|------|------|
| `Flask(__name__)` | 현재 파일 기준으로 Flask 앱 생성 |
| `@app.route('/')` | URL 경로와 함수를 연결하는 데코레이터 |
| `app.run(debug=True)` | 개발용 서버 실행 (코드 수정 시 자동 재시작) |

> ⚠️ `debug=True`는 **개발 중에만** 사용! 배포(운영) 서버에서는 반드시 제거

---

## 3. 라우팅 (Routing)

> **라우팅** = URL 경로에 따라 어떤 함수를 실행할지 연결하는 것

```python
@app.route('/user')         # http://localhost:5000/user
def show_user():
    return "유저 페이지"

@app.route('/admin')        # http://localhost:5000/admin
def show_admin():
    return "관리자 페이지"

@app.route('/product')      # http://localhost:5000/product
def show_product():
    return "상품 페이지"
```

### 하나의 함수에 여러 URL 연결

```python
@app.route('/user')
@app.route('/user/<username>')  # 두 경로 모두 같은 함수 연결
def show_user_profile(username="익명"):
    return f"사용자: {username}"
```

---

## 4. 동적 URL (변수 라우팅)

> URL 안에 `<변수명>`을 넣으면, 그 값이 함수의 파라미터로 전달됨

```python
# 문자열 변수
@app.route('/user/<username>')
def show_user(username):
    return f"사용자: {username}"
# 접속: /user/홍길동  →  "사용자: 홍길동"

# 숫자 변수 (int 타입 지정)
@app.route('/product/<int:id>')
def show_product(id):
    return f"상품코드: {id}"
# 접속: /product/42  →  "상품코드: 42"
```

### 타입 변환기 종류

| 타입 | 표기 | 예시 |
|------|------|------|
| 문자열 (기본) | `<name>` | `/user/alice` |
| 정수 | `<int:id>` | `/product/5` |
| 실수 | `<float:value>` | `/price/3.14` |

### 기본값 설정 (선택적 URL)

```python
@app.route('/user')
@app.route('/user/<username>')
def show_user(username="익명"):   # 기본값 설정
    return f"사용자: {username}"
# /user       →  "사용자: 익명"
# /user/Bob   →  "사용자: Bob"
```

---

## 5. JSON 응답

> **JSON** = 파이썬의 딕셔너리/리스트를 웹에서 주고받는 표준 데이터 형식

```python
from flask import Flask, jsonify

app = Flask(__name__)

users = [
    {'name': 'Alice', 'age': 25},
    {'name': 'Bob',   'age': 30},
]

@app.route('/')
def get_all_users():
    return jsonify(users)   # 리스트 → JSON 변환 후 응답

@app.route('/user/<name>')
def get_user(name):
    for u in users:
        if u['name'].lower() == name.lower():   # 대소문자 무시
            return jsonify(u)
    return jsonify({"message": "사용자를 찾지 못했습니다."})
```

### jsonify() 역할

```
파이썬 딕셔너리/리스트  →  jsonify()  →  JSON 형식 HTTP 응답
{'name': 'Alice'}       →             →  {"name": "Alice"}
```

### 흐름 예시

```
GET /user/alice
      ↓
users 리스트 순회
      ↓
alice 찾으면 → jsonify({'name': 'Alice', 'age': 25}) 반환
못 찾으면   → jsonify({'message': '사용자를 찾지 못했습니다.'}) 반환
```

---

## 6. 전체 흐름 요약

```
[1] 클라이언트(브라우저/앱)가 URL로 요청
         ↓
[2] @app.route() 데코레이터가 URL 매칭
         ↓
[3] 연결된 함수 실행
         ↓
[4] return으로 응답 반환
    - HTML 문자열    →  웹 페이지
    - jsonify(data)  →  JSON 데이터 (API)
```

### 핵심 개념 한눈에 보기

| 개념 | 코드 | 설명 |
|------|------|------|
| 앱 생성 | `Flask(__name__)` | Flask 앱 인스턴스 생성 |
| 라우팅 | `@app.route('/경로')` | URL ↔ 함수 연결 |
| 동적 URL | `<변수명>`, `<int:변수>` | URL 일부를 변수로 받기 |
| HTML 응답 | `return "<h1>...</h1>"` | HTML 문자열 반환 |
| JSON 응답 | `return jsonify(data)` | 딕셔너리/리스트를 JSON으로 변환 |
| 서버 실행 | `app.run(debug=True)` | 개발 서버 시작 |
