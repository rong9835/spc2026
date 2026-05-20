# CRUD 미니앱 핵심 요약

> 이 앱은 Flask + SQLite로 만든 **회원가입 / 로그인 / 정보수정** 미니 웹앱입니다.

---

## CRUD란?

웹앱에서 데이터를 다루는 4가지 기본 동작입니다.

| 이름 | 영어 | SQL | 이 앱에서 하는 일 |
|------|------|-----|------------------|
| 만들기 | **C**reate | INSERT | 회원가입 (새 유저 추가) |
| 읽기 | **R**ead | SELECT | 프로필 조회 |
| 수정 | **U**pdate | UPDATE | 비밀번호 / 이메일 변경 |
| 삭제 | **D**elete | DELETE | (이 앱에는 없음) |

---

## 파일 구조

```
2.crud/
├── app.py                ← 앱의 두뇌 (모든 로직이 여기에)
└── templates/
    ├── base.html         ← 공통 뼈대 (네비게이션 바)
    ├── index.html        ← 홈 화면
    ├── login.html        ← 로그인 폼
    ├── signin.html       ← 회원가입 폼
    └── profile.html      ← 내 정보 수정 폼
```

---

## 핵심 개념 1: 데이터베이스 연결

```python
DATABASE = 'uesrs.sqlite3'   # SQLite 파일 이름

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row   # 결과를 dict처럼 쓸 수 있게
    return conn
```

> **비유**: `sqlite3.connect()`는 서랍장 열기,  
> `conn.row_factory = sqlite3.Row`는 "서랍 번호 대신 이름표로 찾기"  
> → `row[0]` 대신 `row['username']` 처럼 쓸 수 있음

---

## 핵심 개념 2: 테이블 초기화 (`init_db`)

앱이 처음 켜질 때 딱 한 번 실행됩니다.

```python
def init_db():
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email    TEXT
        )
    ''')
```

> **IF NOT EXISTS** = "테이블이 없으면 만들어라"  
> → 앱을 껐다 켜도 데이터가 사라지지 않음

처음 실행 시 기본 계정 2개도 자동 추가됩니다:

```python
if count == 0:   # 유저가 아무도 없을 때만
    INSERT user1 / user2
```

---

## 핵심 개념 3: 라우트(Route) 흐름

```
브라우저 주소창      → Flask 함수      → HTML 파일
/                   → home()          → index.html
/login              → login()         → login.html
/signin             → signin()        → signin.html
/profile            → profile()       → profile.html
/logout             → logout()        → (홈으로 이동)
```

---

## 핵심 개념 4: 회원가입 (CREATE)

`/signin` 에서 POST 요청이 오면:

```python
# 1. 폼 데이터 받기
username = request.form.get("username")

# 2. 이미 있는 아이디인지 확인 (중복 체크)
cur.execute("SELECT * FROM users WHERE username=?", (username,))
existing_user = cur.fetchone()
if existing_user:
    flash("해당 ID는 사용할 수 없습니다.")
    return redirect(...)

# 3. 없으면 DB에 추가 (CREATE)
cur.execute("INSERT INTO users (...) VALUES (?,?,?)", (...))
conn.commit()
```

> **`?` 자리표시자** = SQL 인젝션 공격 방어용  
> 절대 `f"... WHERE username='{username}'"` 처럼 쓰면 안 됨!

---

## 핵심 개념 5: 로그인과 세션

```python
# 1. DB에서 유저 찾기 (READ)
cur.execute("SELECT * FROM users WHERE username=? AND password=?", ...)
user_data = cur.fetchone()

# 2. 있으면 세션에 저장
if user_data:
    session['user'] = username   # 로그인 성공 = 세션에 도장 찍기
```

> **세션(Session)** = 로그인 상태를 서버가 기억하는 임시 메모장  
> 브라우저를 닫거나 5분 지나면 자동 삭제됨 (`timedelta(minutes=5)`)

```python
# 로그아웃 = 세션에서 지우기
session.pop("user", None)
```

---

## 핵심 개념 6: 프로필 수정 (UPDATE)

```python
# 1. 세션에서 현재 로그인한 유저 확인
username = session.get('user', None)
if not username:
    return redirect(url_for("signin"))   # 비로그인 = 접근 차단

# 2. DB 수정 (UPDATE)
if password:
    cur.execute("UPDATE users SET password=? WHERE username=?", (password, username))
if email:
    cur.execute("UPDATE users SET email=? WHERE username=?", (email, username))

conn.commit()   # ← 이걸 해야 실제 저장됨!
```

---

## 핵심 개념 7: flash 메시지

```python
flash("회원가입이 성공적으로 완료되었습니다.")
```

HTML에서 이렇게 받아서 표시:

```html
{% with messages = get_flashed_messages() %}
    {% for msg in messages %}
        <p>{{ msg }}</p>
    {% endfor %}
{% endwith %}
```

> **flash** = 딱 한 번만 보여주는 알림 메시지  
> 페이지를 새로고침하면 사라짐

---

## 핵심 개념 8: base.html 상속

```html
<!-- base.html: 공통 뼈대 -->
<nav>
    {% if 'user' in session %}
        <a href="/logout">Logout</a>   ← 로그인 상태일 때
    {% else %}
        <a href="/login">Login</a>     ← 비로그인 상태일 때
    {% endif %}
</nav>
{% block content %}{% endblock %}   ← 각 페이지 내용이 여기 들어감
```

```html
<!-- index.html: 자식 페이지 -->
{% extends "base.html" %}           ← base.html 물려받기
{% block content %}
    여기에 이 페이지만의 내용
{% endblock %}
```

> **비유**: base.html은 액자 틀, 각 html은 액자 안에 넣는 그림

---

## 전체 흐름 한눈에 보기

```
[처음 실행]
  app.py 실행
    → init_db() 호출
      → DB 파일 없으면 생성
      → users 테이블 없으면 생성
      → 유저 0명이면 기본 계정 2개 추가

[유저 행동]
  회원가입 (/signin POST)
    → DB에 INSERT

  로그인 (/login POST)
    → DB에서 SELECT
    → 맞으면 session['user'] = username

  프로필 보기 (/profile GET)
    → session 확인 → DB에서 SELECT

  정보수정 (/profile POST)
    → DB에서 UPDATE

  로그아웃 (/logout)
    → session에서 user 삭제
```

---

## 주의사항 (실무에서는 이렇게 하면 안 됨)

| 이 앱의 코드 | 실무에서는 |
|-------------|-----------|
| `secret_key = 'hello1234'` | 환경변수로 숨겨야 함 |
| 비밀번호 평문 저장 | bcrypt 등으로 암호화 필요 |
| `debug=True` | 배포 시 반드시 `False`로 변경 |

> 이 앱은 **학습용**이라 단순하게 만든 것입니다.
