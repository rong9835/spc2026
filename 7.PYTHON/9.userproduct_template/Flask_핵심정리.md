# Flask 사용자/상품 조회 앱 핵심정리

## 프로젝트 구조

```
9.userproduct_template/
├── app.py
└── templates/
    ├── index.html
    ├── user.html
    └── product.html
```

---

## 1. URL 파라미터 vs 쿼리 파라미터

Flask에서 URL로 값을 받는 방법은 두 가지다.

| 구분 | URL 예시 | 사용 상황 |
|------|----------|-----------|
| **URL 파라미터** | `/user/1` | 특정 리소스를 ID로 조회할 때 |
| **쿼리 파라미터** | `/product?id=101` | 검색 조건이 여러 개일 때 |

### URL 파라미터 (Path Parameter)

```python
@app.route('/user')          # /user → 전체 조회
@app.route('/user/<int:user_id>')  # /user/1 → 특정 조회
def user(user_id=None):
    ...
```

- `<int:user_id>` : URL에서 정수를 받아 `user_id` 변수에 저장
- 라우트를 두 개 걸어서 하나의 함수로 처리
- `user_id=None` : URL 파라미터가 없을 때 기본값

### 쿼리 파라미터 (Query Parameter)

```python
@app.route('/product')
def product():
    id   = request.args.get('id',   type=int)   # ?id=101
    name = request.args.get('name', type=str)   # ?name=Laptop
```

- `request.args.get('키', type=타입)` 으로 값을 꺼냄
- 값이 없으면 `None` 반환 (기본값 설정 가능)
- 여러 조건을 동시에 처리하기 편함

---

## 2. dict 안에 dict (데이터 저장 방식)

```python
users = {
    1: {"id": 1, "name": "홍길동", "email": "hong@example.com"},
    2: {"id": 2, "name": "김철수", "email": "kim@example.com"},
}
```

### 왜 이렇게 쓰나?

```python
# 리스트 방식 → 전체를 순회해야 함 (느림)
for u in users_list:
    if u["id"] == 1: ...

# dict 방식 → 키로 바로 접근 (빠름)
user = users[1]  # O(1) 즉시 조회
user = users.get(1)  # 없으면 None 반환 (안전)
```

> **핵심:** ID가 키인 dict를 쓰면 `users[1]` 한 줄로 조회 완료

---

## 3. render_template — 템플릿에 데이터 전달

```python
return render_template("user.html", user_id=user_id, users=users)
```

- `"user.html"` : templates 폴더 안의 파일명
- `user_id=user_id` : 템플릿에서 `user_id` 변수로 사용 가능
- `users=users` : 템플릿에서 `users` 딕셔너리 사용 가능

---

## 4. Jinja2 템플릿 문법

HTML 안에서 파이썬처럼 조건문/반복문을 쓸 수 있다.

### 변수 출력 `{{ }}`

```html
{{ u.name }}     <!-- 변수 값 출력 -->
{{ u.id }}
```

### 조건문 `{% if %}`

```html
{% if user_id %}
    <!-- user_id가 있을 때 -->
{% else %}
    <!-- user_id가 없을 때 (전체 목록) -->
{% endif %}
```

### 반복문 `{% for %}`

```html
{% for u in users.values() %}
    <li>{{ u.name }}</li>
{% endfor %}
```

### 변수 선언 `{% set %}`

```html
{% set u = users.get(user_id) %}
{% if u %}
    <li>{{ u.name }}</li>
{% endif %}
```

> `users.get(user_id)` : 키가 없으면 None (KeyError 없이 안전)

---

## 5. 검색 폼 처리

### user.html — JS로 URL 이동 (GET)

```html
<form onsubmit="event.preventDefault(); location.href='/user/' + document.getElementById('id').value">
    <input type="number" id="id">
    <button type="submit">검색</button>
</form>
```

- 폼 제출 시 기본 동작 막고, JS로 `/user/1` 형태의 URL로 이동
- URL 파라미터 방식이라 JS가 필요

### product.html — HTML 폼 기본 GET (쿼리 파라미터)

```html
<form>
    <input type="number" name="id"   value="{{ request.args.get('id', '') }}">
    <input type="text"   name="name" value="{{ request.args.get('name', '') }}">
    <button type="submit">검색</button>
</form>
```

- `<form>` 기본 method는 GET → 자동으로 `?id=101&name=Laptop` 생성
- `value="{{ request.args.get('id', '') }}"` : 검색 후 입력값 유지

---

## 6. 상품 필터링 로직

```python
found = list(products.values())   # 전체 상품 리스트

if id:
    found = [p for p in found if p["id"] == id]

if name:
    found = [p for p in found if p["name"].lower() == name.lower()]
```

- 조건이 없으면 전체, 있으면 해당 조건으로 필터
- `.lower()` 로 대소문자 구분 없이 비교
- 리스트 컴프리헨션으로 간결하게 필터링

---

## 전체 흐름 요약

```
브라우저 요청
    ↓
Flask 라우터 (@app.route)
    ↓
뷰 함수 실행 (URL파라미터 or 쿼리파라미터 파싱)
    ↓
데이터 조회 (dict 인덱싱 or 리스트 필터링)
    ↓
render_template("템플릿.html", 변수=값)
    ↓
Jinja2가 HTML 생성 ({{ }}, {% %})
    ↓
브라우저에 HTML 응답
```

---

## 핵심 포인트 한눈에 보기

| 개념 | 코드 | 설명 |
|------|------|------|
| URL 파라미터 | `@app.route('/user/<int:id>')` | `/user/1` |
| 쿼리 파라미터 | `request.args.get('id', type=int)` | `?id=1` |
| 안전한 dict 조회 | `users.get(user_id)` | 없으면 None |
| 템플릿 변수 출력 | `{{ u.name }}` | 값 출력 |
| 템플릿 조건문 | `{% if %}...{% endif %}` | 조건 분기 |
| 템플릿 반복문 | `{% for u in users.values() %}` | 반복 출력 |
| 다중 라우트 | `@app.route` 두 번 | 한 함수에 여러 URL |
