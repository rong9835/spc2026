# 🍪 쿠키(Cookie) 핵심 정리

---

## 1. 쿠키란?

> **브라우저(손님)가 정보를 들고 다니는 메모지**

서버는 기본적으로 **누가 왔는지 기억하지 못합니다.**  
(HTTP는 요청이 끝나면 연결이 끊어지는 **무상태(Stateless)** 방식)

쿠키는 이 문제를 해결합니다.

```
서버 → "이 메모 들고 다녀!" → 브라우저에 쿠키 저장
브라우저 → 다음 요청 때 메모 자동으로 들고 옴
서버 → "아, 너구나!" → 사용자 식별 가능
```

---

## 2. 쿠키의 흐름

```
[1] 클라이언트(브라우저)가 서버에 요청
        ↓
[2] 서버가 응답할 때 Set-Cookie 헤더로 쿠키 전달
        ↓
[3] 브라우저가 쿠키를 자동 저장
        ↓
[4] 이후 요청마다 브라우저가 자동으로 Cookie 헤더에 담아 전송
        ↓
[5] 서버가 쿠키를 읽어서 사용자 식별
```

---

## 3. Flask 쿠키 실습 코드 분석

```python
from flask import Flask, make_response, request

app = Flask(__name__)
```

| 임포트 | 역할 |
|--------|------|
| `Flask` | 웹 앱 생성 |
| `make_response` | 응답 객체를 직접 만들 때 사용 (쿠키 세팅에 필요) |
| `request` | 클라이언트가 보낸 요청 정보 접근 |

---

### ✅ 쿠키 저장하기 `/set-cookie`

```python
@app.route("/set-cookie")
def set_cookie():
    resp = make_response("Cookie has been set!!")  # 응답 객체 생성
    resp.set_cookie("my-edu", "spc2026")           # 쿠키 이름="my-edu", 값="spc2026"
    return resp
```

**핵심 포인트:**
- 쿠키를 저장할 때는 `return "문자열"` 대신 **`make_response()`** 로 응답 객체를 먼저 만들어야 함
- `set_cookie("키", "값")` 으로 쿠키 설정

---

### ✅ 쿠키 읽기 `/get-cookie`

```python
@app.route("/get-cookie")
def get_cookie():
    cookie = request.cookies.get('my-edu')  # 'my-edu' 쿠키 읽기
    return f"안녕, {cookie} 야"
```

**핵심 포인트:**
- `request.cookies` → 브라우저가 보낸 모든 쿠키가 담긴 딕셔너리
- `.get('키이름')` → 해당 쿠키 값 가져오기 (없으면 None 반환)

---

## 4. 쿠키 vs 세션 비교

| 구분 | 쿠키 | 세션 |
|------|------|------|
| 저장 위치 | **브라우저** (클라이언트) | **서버** |
| 보안 | 낮음 (유저가 볼 수 있음) | 높음 (서버에만 있음) |
| 용량 | 최대 4KB | 서버 용량 제한 |
| 만료 | 직접 설정 가능 | 브라우저 종료 시 삭제 (기본) |
| 예시 | 자동 로그인, 장바구니 | 로그인 상태 유지 |

---

## 5. set_cookie() 주요 옵션

```python
resp.set_cookie(
    "키",
    "값",
    max_age=3600,      # 유효 시간 (초 단위, 3600 = 1시간)
    expires=날짜,       # 만료 날짜
    secure=True,       # HTTPS에서만 전송
    httponly=True,     # JS에서 접근 불가 (보안 강화)
    samesite='Lax'     # CSRF 공격 방지
)
```

---

## 6. 쿠키 삭제

```python
@app.route("/delete-cookie")
def delete_cookie():
    resp = make_response("쿠키 삭제됨")
    resp.delete_cookie("my-edu")  # 쿠키 삭제
    return resp
```

---

## 7. 비유로 이해하기

```
🏪 편의점 (서버)
👤 손님 (브라우저)
🏷️ 쿠폰카드 (쿠키)

1. 손님이 처음 방문 → 편의점이 쿠폰카드 발급 (set_cookie)
2. 손님이 카드를 지갑에 보관 (브라우저 저장)
3. 다음 방문 시 카드 자동 제시 (자동으로 Cookie 헤더 전송)
4. 편의점이 카드 확인 후 "단골이시네요!" (request.cookies.get)
```

---

## 8. 실행 방법

```bash
# 서버 실행
python app.py

# 브라우저에서 테스트
http://127.0.0.1:5000/set-cookie   # 쿠키 저장
http://127.0.0.1:5000/get-cookie   # 쿠키 읽기
```

---

## 9. 핵심 요약

| 작업 | 코드 |
|------|------|
| 쿠키 저장 | `resp = make_response(...)` → `resp.set_cookie("키", "값")` |
| 쿠키 읽기 | `request.cookies.get("키")` |
| 쿠키 삭제 | `resp.delete_cookie("키")` |

> **기억할 것:** 쿠키는 **브라우저**에 저장, 세션은 **서버**에 저장!
