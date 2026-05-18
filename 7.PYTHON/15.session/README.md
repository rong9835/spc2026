# 15. 세션(Session) 핵심 정리

---

## 세션이란?

> **쿠키**는 정보를 **브라우저(내 컴퓨터)** 에 저장 → 사용자가 볼 수 있고 위변조 가능  
> **세션**은 정보를 **서버** 에 저장하고, 브라우저엔 "열쇠(ID)"만 줌 → 더 안전!

```
[브라우저]  ←→  [서버]
  쿠키: "열쇠(세션ID)"만 보관     세션 데이터: "진짜 정보" 보관
```

---

## 파일별 핵심 내용

### 1️⃣ 1.app.py — 세션 기본 사용

Flask 기본 세션 (쿠키에 암호화해서 저장하는 방식)

```python
from flask import Flask, session

app.secret_key = 'your_secret_key'  # 암호화 키 (꼭 필요!)

# 세션에 저장
session['username'] = 'spc2026'

# 세션에서 읽기
if 'username' in session:
    return session['username']
```

| 포인트 | 설명 |
|--------|------|
| `secret_key` | 세션 데이터를 암호화하는 비밀 열쇠. 없으면 세션 못 씀 |
| `session['키'] = 값` | 세션에 데이터 저장 |
| `'키' in session` | 세션에 데이터가 있는지 확인 |

---

### 2️⃣ 2.app_store.py — 서버 파일에 세션 저장 (flask-session)

기본 세션은 쿠키에 저장 → 용량 작고 보안 약함  
`flask-session`을 쓰면 **서버 파일/DB에 저장** 가능!

```bash
pip install flask-session
```

```python
from flask_session import Session

app.config['SESSION_TYPE'] = 'filesystem'   # 파일로 저장
app.config['SESSION_FILE_DIR'] = './sessions'  # 저장 폴더
app.config['SESSION_PERMANENT'] = False     # 브라우저 닫으면 삭제
app.config['SESSION_USE_SIGNER'] = True     # 쿠키에 서명 추가

Session(app)  # 세션 초기화
```

| 설정값 | 의미 |
|--------|------|
| `SESSION_TYPE` | 저장 방식: `filesystem`, `redis`, `mongodb` 등 |
| `SESSION_PERMANENT` | `False` = 브라우저 닫으면 사라짐 |
| `SESSION_USE_SIGNER` | 위변조 방지 서명 사용 |

---

### 3️⃣ 3.app_store.py — 첫 방문 / 재방문 구분

```python
@app.route('/')
def main():
    if 'username' in session:        # 세션이 있으면 = 재방문
        return f"다시 오셨군요! {session['username']}"

    # 세션이 없으면 = 첫 방문
    session['username'] = 'spc2026'
    return "첫 방문이시군요. 당신을 기억하겠습니다."
```

**흐름 요약:**
```
첫 방문 → 세션 없음 → 세션 생성 → "첫 방문이시군요"
재방문  → 세션 있음 →              "다시 오셨군요"
```

---

### 4️⃣ 4.login.py — 세션으로 로그인 시스템 구현 ⭐

가장 실용적인 예제! 로그인 → 세션 저장 → 인증 확인 → 로그아웃

#### 전체 흐름

```
[로그인 폼] → ID/PW 입력 → 서버에서 확인
                              ↓ 맞으면
                          session['user'] = 사용자 정보 저장
                              ↓
                          /dashboard 이동 (세션으로 이름 표시)
```

#### 주요 기능별 코드

**① 로그인 처리**
```python
@app.route('/', methods=['POST'])
def login():
    id = request.form.get('id')
    pw = request.form.get('pw')

    # users 목록에서 일치하는 사용자 찾기
    user = next((u for u in users if u['id'] == id and u['pw'] == pw), None)

    if user:
        session['user'] = user      # 세션에 사용자 저장
        return redirect(url_for('welcome'))
    else:
        return render_template('index.html', error="Invalid ID or password")
```

**② 로그인 여부 확인 (페이지 보호)**
```python
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user = session.get('user')
    if not user:
        return redirect(url_for('home'))  # 로그인 안됐으면 강제 이동!
```

**③ 로그아웃**
```python
@app.route('/logout')
def logout():
    session.pop('user', None)  # 세션에서 user 삭제
    return redirect(url_for('home'))
```

**④ 비밀번호 변경 후 세션 갱신**
```python
u['pw'] = new_pw          # DB(리스트)에서 비번 변경
session['user'] = u       # 세션도 새 정보로 업데이트!
```

> 세션을 업데이트 안 하면 로그인된 사용자 정보가 옛날 비번을 계속 가지고 있게 됨!

---

## 쿠키 vs 세션 한눈에 비교

| 구분 | 쿠키 | 세션 |
|------|------|------|
| 저장 위치 | 브라우저(내 컴퓨터) | 서버 |
| 보안 | 낮음 (사용자가 볼 수 있음) | 높음 (서버에만 있음) |
| 용량 | 4KB 제한 | 제한 없음 |
| 만료 | 직접 설정 | 브라우저 닫으면 사라짐 (기본) |
| 사용 예 | 자동 로그인, 언어 설정 | 로그인 유지, 장바구니 |

---

## 세션 핵심 메서드 정리

```python
session['key'] = value      # 저장
session.get('key')          # 읽기 (없으면 None 반환)
'key' in session            # 존재 여부 확인
session.pop('key', None)    # 삭제 (없어도 오류 안 남)
session.clear()             # 전체 삭제
```

---

## 페이지 구성 (4.login.py 기준)

```
/           GET  → 로그인 폼 (이미 로그인이면 /dashboard로 이동)
/           POST → 로그인 처리
/dashboard       → 로그인한 사람만 볼 수 있는 페이지
/profile    GET  → 내 정보 보기
/profile    POST → 비밀번호 변경
/logout          → 로그아웃 (세션 삭제)
```
