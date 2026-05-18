# 13. Flask 로그인 구현

## 전체 흐름 한눈에 보기

```
사용자가 폼 제출
      ↓
Flask가 POST 요청 받음
      ↓
입력한 ID/PW를 users 목록과 비교
      ↓
일치하면 → 환영 메시지 출력
불일치 → 에러 메시지 출력
```

---

## 핵심 개념

### 1. GET vs POST

| 방식 | 언제 쓰나? | 특징 |
|------|-----------|------|
| **GET** | 페이지를 처음 열 때 | URL에 데이터가 보임 |
| **POST** | 폼을 제출할 때 | 데이터가 숨겨져 전송됨 |

> 로그인 폼은 **POST** 방식을 써야 비밀번호가 URL에 노출되지 않음!

---

### 2. app.py 핵심 코드

#### 사용자 DB (메모리에 저장)
```python
users = [
    {'name': '홍길동', 'id': 'hong', 'pw': '1234'},
    {'name': '고길동', 'id': 'gil',  'pw': 'abcd'},
    {'name': '김길동', 'id': 'dong', 'pw': 'qwe123'},
]
```
- 실제 서비스에선 데이터베이스(DB)에 저장
- 지금은 학습용으로 리스트에 직접 넣어둠

#### 라우트 (GET + POST 동시 처리)
```python
@app.route('/', methods=['GET', 'POST'])  # GET과 POST 둘 다 허용
def home():
    if request.method == 'POST':          # POST일 때만 로그인 처리
        id = request.form['id']           # 폼에서 id 값 꺼내기
        pw = request.form['pw']           # 폼에서 pw 값 꺼내기
```

> `request.form['필드명']` → HTML `<input name="필드명">` 과 짝을 이룸

#### 로그인 검증 로직
```python
user = None
for u in users:                          # users 목록을 하나씩 확인
    if u['id'] == id and u['pw'] == pw:  # ID와 PW 모두 일치하면
        user = u                         # 해당 사용자 저장

if user:
    error = None           # 로그인 성공
else:
    error = "Invalid ID or PW"  # 로그인 실패
```

---

### 3. index.html 핵심 코드

#### Jinja2 조건문으로 화면 분기
```html
{% if user %}
    <h2>안녕하세요, {{ user.name }} 님</h2>   <!-- 로그인 성공 -->
{% else %}
    <form method="POST"> ... </form>           <!-- 로그인 폼 보여줌 -->
    {% if error %}
        <p style="color:red">{{ error }}</p>   <!-- 에러 메시지 -->
    {% endif %}
{% endif %}
```

> `{{ }}` → 값 출력  
> `{% %}` → 조건/반복 등 로직 처리

---

## 전체 동작 시나리오

### 성공 케이스
```
1. 브라우저에서 / 접속 (GET)
   → 로그인 폼 화면 표시

2. hong / 1234 입력 후 제출 (POST)
   → users에서 hong 찾기 성공
   → user = {'name': '홍길동', ...}

3. 템플릿에 user 전달
   → "안녕하세요, 홍길동 님" 출력
```

### 실패 케이스
```
1. wrong / 9999 입력 후 제출 (POST)
   → users에서 일치하는 항목 없음
   → user = None, error = "Invalid ID or PW"

2. 템플릿에 error 전달
   → 빨간 글씨로 에러 메시지 출력
   → 폼은 그대로 유지
```

---

## Flask → 템플릿 데이터 전달

```python
# app.py
return render_template('index.html', user=user, error=error)
#                                    ↑변수명    ↑변수명
```

```html
<!-- index.html -->
{{ user.name }}  <!-- user 변수의 name 속성 출력 -->
{{ error }}      <!-- error 변수 출력 -->
```

> `render_template()` 의 키워드 인자 이름 = 템플릿에서 쓰는 변수 이름

---

## 주의할 점 (실무에서는)

| 이 코드의 문제점 | 실무에서는 |
|----------------|-----------|
| 비밀번호를 평문으로 저장 | bcrypt 등으로 **해시 처리** |
| 사용자 정보를 메모리에 저장 | **데이터베이스** 사용 |
| 로그인 상태 유지 안 됨 | **세션(Session)** 또는 **쿠키** 사용 |
| 비밀번호가 코드에 하드코딩 | **환경변수** 또는 DB에 저장 |

---

## 실행 방법

```bash
cd 7.PYTHON/13.login
python app.py
# → http://127.0.0.1:5000 접속
```

**테스트 계정**
- `hong` / `1234`
- `gil` / `abcd`
- `dong` / `qwe123`
