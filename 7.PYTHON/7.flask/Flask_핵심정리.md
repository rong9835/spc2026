# Flask 핵심 정리

## 목차
1. [Flask란?](#1-flask란)
2. [기본 앱 구조](#2-기본-앱-구조)
3. [라우팅 (Route)](#3-라우팅-route)
4. [JSON 응답 (jsonify)](#4-json-응답-jsonify)
5. [쿼리 파라미터 (Query Parameter)](#5-쿼리-파라미터-query-parameter)
6. [템플릿 (Jinja2)](#6-템플릿-jinja2)
7. [폼 데이터 처리 (POST)](#7-폼-데이터-처리-post)
8. [파일 업로드](#8-파일-업로드)
9. [디렉토리 구조](#9-디렉토리-구조)

---

## 1. Flask란?

**Flask**는 파이썬으로 웹 서버(백엔드)를 만드는 경량 프레임워크입니다.

```
사용자(브라우저) → 요청(Request) → Flask 서버 → 응답(Response) → 화면 출력
```

```bash
pip install flask
```

---

## 2. 기본 앱 구조

```python
from flask import Flask

app = Flask(__name__)   # Flask 앱 생성

@app.route('/')         # 어떤 URL로 접속했을 때
def home():             # 실행할 함수
    return "<h1>Hello!</h1>"   # 응답 내용

if __name__ == '__main__':
    app.run(debug=True)  # 서버 실행 (debug=True: 코드 변경 시 자동 재시작)
```

> **주의**: `debug=True`는 개발 중에만! 운영 서버 배포 시 반드시 제거

---

## 3. 라우팅 (Route)

URL 패턴에 따라 다른 함수를 실행하는 것.

### 기본 라우팅

```python
@app.route('/user')
def show_user():
    return "사용자 페이지"
```

### URL 변수 (Path Parameter)

URL에 값을 직접 포함시켜 받는 방식.

```python
# /user/Alice → username = "Alice"
@app.route('/user/<username>')
def show_user(username):
    return f"사용자: {username}"

# /product/5 → id = 5 (숫자 타입으로 자동 변환)
@app.route('/product/<int:id>')
def show_product(id):
    return f"상품코드: {id}"
```

| 타입 변환자 | 설명 |
|---|---|
| `<username>` | 기본값 (문자열) |
| `<int:id>` | 정수형으로 변환 |
| `<float:price>` | 실수형으로 변환 |

### 여러 URL을 하나의 함수에 연결

```python
@app.route('/user')
@app.route('/user/<username>')   # 두 URL 모두 같은 함수 실행
def show_user(username="익명"):  # 기본값 설정
    return f"사용자: {username}"
```

---

## 4. JSON 응답 (jsonify)

파이썬 `list` / `dict` 데이터를 웹 표준 **JSON 형식**으로 변환해서 응답.

```python
from flask import Flask, jsonify

users = [
    {'name': 'Alice', 'age': 25},
    {'name': 'Bob',   'age': 30},
]

@app.route('/')
def get_users():
    return jsonify(users)   # 파이썬 리스트 → JSON 배열
```

### 특정 사용자 찾아서 반환

```python
@app.route('/user/<name>')
def get_user(name):
    for u in users:
        if u['name'].lower() == name.lower():   # 대소문자 무시
            return jsonify(u)
    return jsonify({"message": "User not found"})
```

---

## 5. 쿼리 파라미터 (Query Parameter)

URL 뒤에 `?키=값` 형식으로 검색 조건 전달.

```
/search?q=파이썬&page=2
          ↑ q라는 키로 "파이썬" 전달, page는 2
```

```python
from flask import request

@app.route('/search')
def search():
    query = request.args.get('q')                    # 필수 파라미터
    page  = request.args.get('page', default=1, type=int)  # 기본값 1, 정수형
    return jsonify({"query": query, "page": page})
```

### 여러 조건으로 필터링 (검색 기능)

```python
@app.route('/search')
def search_user():
    name  = request.args.get('name')
    age   = request.args.get('age')
    phone = request.args.get('phone')

    result = users  # 전체 목록에서 시작

    if name:
        result = [u for u in result if name.lower() in u['name'].lower()]

    if age:
        result = [u for u in result if int(age) == u['age']]

    if phone:
        result = [u for u in result if u['phone'].startswith(phone)]  # 앞자리로 검색

    return jsonify(result)
```

> **요청 예시**: `/search?name=alice&age=25`

---

## 6. 템플릿 (Jinja2)

HTML 파일을 별도로 분리하고, 파이썬 데이터를 HTML에 삽입하는 방식.

### 파일 구조

```
프로젝트/
├── app.py
└── templates/       ← HTML 파일은 반드시 여기에!
    └── index.html
```

### Python 코드

```python
from flask import render_template

@app.route('/')
def index():
    names = ["홍길동", "고길동", "김길동"]
    return render_template('users.html', names=names)  # 변수 전달
```

### HTML 템플릿 (Jinja2 문법)

```html
<ul>
    {% for name in names %}       <!-- 반복문 -->
    <li>{{ name }}</li>           <!-- 변수 출력 -->
    {% endfor %}                  <!-- 반복문 종료 -->
</ul>
```

### 딕셔너리 리스트 출력

```python
# Python
users = [
    {'name': '홍길동', 'age': 25, 'phone': '123-456-7890'},
    {'name': '고길동', 'age': 30, 'phone': '123-555-7890'},
]
return render_template('users_detail.html', users=users)
```

```html
<!-- HTML -->
{% for user in users %}
<li>{{ user['name'] }}</li>
<ul>
    <li>나이: {{ user['age'] }}</li>
    <li>전화번호: {{ user['phone'] }}</li>
</ul>
{% endfor %}
```

### Jinja2 핵심 문법 요약

| 문법 | 용도 |
|---|---|
| `{{ 변수 }}` | 변수 출력 |
| `{% for x in list %}` | 반복문 시작 |
| `{% endfor %}` | 반복문 종료 |
| `{% if 조건 %}` | 조건문 시작 |
| `{% endif %}` | 조건문 종료 |

---

## 7. 폼 데이터 처리 (POST)

HTML 폼(로그인, 회원가입 등)에서 입력한 데이터를 서버로 전송하는 방식.

### HTML 폼

```html
<form method="POST" action="/login">
    <input type="text"     name="id" placeholder="아이디">
    <input type="password" name="pw" placeholder="비밀번호">
    <button type="submit">로그인</button>
</form>
```

### Python - POST 처리

```python
@app.route('/login', methods=['POST'])   # POST 방식만 허용
def login():
    id = request.form.get('id')   # HTML의 name="id"와 일치
    pw = request.form.get('pw')   # HTML의 name="pw"와 일치
    return render_template('login.html', name=id)
```

### GET vs POST 비교

| | GET | POST |
|---|---|---|
| 데이터 위치 | URL (`?key=value`) | 요청 본문 (Body) |
| 사용 용도 | 조회, 검색 | 로그인, 회원가입, 데이터 생성 |
| 보안 | 낮음 (URL에 노출) | 높음 |
| 데이터 크기 | 제한 있음 | 제한 없음 |

---

## 8. 파일 업로드

이미지/파일을 서버에 저장하는 방법.

```python
import os
from flask import request

app.config['UPLOAD_FOLDER'] = 'uploads'           # 저장 폴더 설정
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # 폴더 없으면 자동 생성

def allowed_file(filename):
    ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif'}   # 허용 확장자
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['photo']   # HTML input name="photo"

    if file and allowed_file(file.filename):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)         # 파일 저장
        return "업로드 성공"
    else:
        return "지원되지 않는 파일 형식"
```

> **실서비스 주의사항**: 파일명 중복 방지를 위해 저장 시 이름을 바꿔야 함
> 예) `타임스탬프_userid_원본파일명.jpg` 형식 사용

---

## 9. 디렉토리 구조

```
flask_project/
├── app.py                 ← 메인 파이썬 파일
├── uploads/               ← 업로드 파일 저장
│   └── image.jpg
└── templates/             ← HTML 템플릿 (반드시 이 이름!)
    ├── index.html
    ├── users.html
    ├── users_detail.html
    ├── form.html
    └── login.html
```

---

## 전체 흐름 요약

```
브라우저 요청
    ↓
URL 패턴 매칭 (@app.route)
    ↓
뷰 함수 실행
    ↓
데이터 처리 (request.args / request.form / request.files)
    ↓
응답 생성 (jsonify / render_template / return 문자열)
    ↓
브라우저 화면 출력
```

| 요청 방식 | 데이터 접근 | 주요 용도 |
|---|---|---|
| URL 변수 | `<int:id>` | 특정 리소스 조회 |
| 쿼리 파라미터 | `request.args.get()` | 검색, 필터, 페이징 |
| 폼 데이터 | `request.form.get()` | 로그인, 회원가입 |
| 파일 업로드 | `request.files[]` | 이미지/파일 업로드 |
