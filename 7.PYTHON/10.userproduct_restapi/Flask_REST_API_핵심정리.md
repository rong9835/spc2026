# Flask REST API 핵심정리

## 프로젝트 구조

```
10.userproduct_restapi/
├── app.py              ← Flask 서버 (API + 라우팅)
└── static/
    ├── index.html      ← 메인 페이지
    ├── user.html       ← 사용자 검색 페이지
    └── product.html    ← 상품 조회 페이지
```

---

## 핵심 개념 1 — URL 파라미터 vs 쿼리 파라미터

| 구분 | 형태 | 사용 목적 | 예시 |
|------|------|-----------|------|
| **URL 파라미터** | `/user/1` | 특정 한 개 조회 | `/api/user/3` → id=3 사용자 |
| **쿼리 파라미터** | `/product?id=101` | 조건부 검색/필터 | `/api/product?name=Laptop` |

```python
# URL 파라미터: <id> 로 받음
@app.route('/api/user/<id>')
def search_user(id):          # id가 함수 인자로 자동 전달
    ...

# 쿼리 파라미터: request.args 로 받음
@app.route('/api/product')
def search_product():
    id   = request.args.get('id')    # ?id=101
    name = request.args.get('name')  # ?name=Laptop
    ...
```

---

## 핵심 개념 2 — dict 안에 dict (중첩 딕셔너리)

```python
users = {
    1: {"id": 1, "name": "홍길동", "email": "hong@example.com"},
    2: {"id": 2, "name": "김철수", "email": "kim@example.com"},
    ...
}
```

### 왜 dict 안에 dict를 쓰나?

```python
# ❌ 리스트 방식 → 처음부터 끝까지 순회해야 함 (느림)
for u in users:
    if u["id"] == 3:
        return u

# ✅ dict 방식 → 키로 바로 접근 (빠름)
user = users.get(3)   # O(1) 즉시 조회
```

> 데이터가 많을수록 dict 방식이 훨씬 빠르다.

---

## 핵심 개념 3 — 정적 페이지 vs API 분리

```
브라우저 주소창 입력       →  정적 HTML 페이지 반환
/                          →  index.html
/user                      →  user.html
/product                   →  product.html

JavaScript fetch 호출      →  JSON 데이터 반환
/api/user/<id>             →  {"result": {...}}
/api/product               →  {"result": [...]}
```

```python
# 정적 페이지 라우팅: HTML 파일을 그대로 전달
@app.route('/user')
def user():
    return send_from_directory("static", "user.html")

# API 라우팅: JSON 데이터 반환
@app.route('/api/user/<id>')
def search_user(id):
    user = users.get(int(id))
    return jsonify({"result": user})
```

---

## 핵심 개념 4 — jsonify

```python
from flask import jsonify

# Python dict → JSON 응답으로 자동 변환
return jsonify({"result": user})

# 응답 결과 (브라우저/fetch가 받는 것)
# {"result": {"id": 1, "name": "홍길동", "email": "hong@example.com"}}
```

---

## 핵심 개념 5 — 프론트와 백엔드 연결 흐름

```
[user.html]
  ↓ 1. 사용자가 ID 입력 후 검색 버튼 클릭
  ↓ 2. JavaScript가 fetch('/api/user/3') 호출
  ↓ 3. Flask가 /api/user/<id> 라우트에서 처리
  ↓ 4. JSON으로 응답 {"result": {"id": 3, "name": "이영희"}}
  ↓ 5. JavaScript가 받아서 화면에 표시
```

```javascript
// user.html의 JavaScript 코드
fetch(`/api/user/${id}`)         // 서버에 요청
    .then(resp => resp.json())   // JSON으로 파싱
    .then(data => console.log(data)); // 데이터 활용
```

---

## 전체 app.py 완성 예시

```python
from flask import Flask, send_from_directory, request, jsonify

app = Flask(__name__)

users = {
    1: {"id": 1, "name": "홍길동", "email": "hong@example.com"},
    2: {"id": 2, "name": "김철수", "email": "kim@example.com"},
    3: {"id": 3, "name": "이영희", "email": "lee@example.com"},
}

products = {
    101: {"id": 101, "name": "Laptop",   "price": 1200},
    102: {"id": 102, "name": "Keyboard", "price": 80},
    103: {"id": 103, "name": "Mouse",    "price": 40},
}

# ── 정적 페이지 ───────────────────────────
@app.route("/")
def home():
    return send_from_directory("static", "index.html")

@app.route('/user')
def user():
    return send_from_directory("static", "user.html")

@app.route('/product')
def product():
    return send_from_directory("static", "product.html")

# ── API ──────────────────────────────────
@app.route('/api/user/<id>')
def search_user(id):
    user = users.get(int(id))          # dict에서 즉시 조회
    return jsonify({"result": user})   # 없으면 None 반환

@app.route('/api/product')
def search_product():
    id   = request.args.get('id')
    name = request.args.get('name')

    if id:
        result = products.get(int(id))
        return jsonify({"result": result})

    if name:
        result = [p for p in products.values() if p["name"] == name]
        return jsonify({"result": result})

    # 파라미터 없으면 전체 반환
    return jsonify({"result": list(products.values())})

if __name__ == "__main__":
    app.run(debug=True)
```

---

## 한눈에 보는 API 엔드포인트 정리

| 경로 | 메서드 | 설명 | 예시 |
|------|--------|------|------|
| `/api/user/<id>` | GET | 특정 사용자 조회 | `/api/user/1` |
| `/api/product` | GET | 전체 상품 조회 | `/api/product` |
| `/api/product?id=101` | GET | ID로 상품 검색 | `/api/product?id=102` |
| `/api/product?name=Laptop` | GET | 이름으로 상품 검색 | `/api/product?name=Mouse` |

---

## 자주 쓰는 Flask 함수 요약

```python
send_from_directory("폴더", "파일명")  # HTML 파일 반환
request.args.get("키")                 # 쿼리 파라미터 읽기
jsonify({"key": value})               # dict → JSON 응답
```
