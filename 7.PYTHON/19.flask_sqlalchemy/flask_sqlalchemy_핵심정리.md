# Flask SQLAlchemy 핵심 정리

> **대상**: 파이썬 입문자
> **한 줄 요약**: Flask 웹앱에서 데이터베이스를 파이썬 코드로 쉽게 다루는 도구

---

## 1. Flask SQLAlchemy가 뭔가요?

### 쉬운 비유로 이해하기

> 데이터베이스 = **엑셀 파일**
> 테이블 = **엑셀 시트 (탭)**
> 행(Row) = **시트의 한 줄 (한 사람의 정보)**
> 열(Column) = **시트의 열 (이름, 나이 등 항목)**

보통 데이터베이스를 다루려면 **SQL**이라는 언어를 써야 합니다:
```sql
SELECT * FROM users WHERE age > 20;
```

SQLAlchemy를 쓰면 파이썬 코드로 똑같이 할 수 있습니다:
```python
User.query.filter(User.age > 20).all()
```

---

## 2. 설치

```bash
pip install flask-sqlalchemy
```

---

## 3. 전체 구조 한눈에 보기

```
1. db 객체 생성       → SQLAlchemy()
2. 모델(테이블) 정의  → class User(db.Model)
3. Flask 앱 설정      → app.config[...]
4. db와 app 연결      → db.init_app(app)
5. 테이블 생성        → db.create_all()
6. 데이터 조회/추가   → User.query, db.session
```

---

## 4. 코드 단계별 설명

### Step 1 - db 객체 먼저 만들기

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # 아직 Flask 앱과 연결 안 된 상태
```

> 마치 빈 엑셀 프로그램을 켜둔 것. 아직 파일을 열지 않은 상태.

---

### Step 2 - 테이블 구조 정의 (모델 클래스)

```python
class User(db.Model):
    __tablename__ = 'users'           # 테이블 이름
    id   = db.Column(db.Integer, primary_key=True)  # 고유 번호 (자동 증가)
    name = db.Column(db.String(80), nullable=False)  # 이름 (필수)
    age  = db.Column(db.Integer, nullable=True)      # 나이 (선택)
```

**컬럼 타입 종류**

| 타입 | 의미 | 예시 |
|------|------|------|
| `db.Integer` | 정수 | 1, 20, 100 |
| `db.String(n)` | 문자열 (최대 n글자) | "홍길동" |
| `db.Float` | 소수 | 3.14 |
| `db.Boolean` | 참/거짓 | True / False |
| `db.DateTime` | 날짜+시간 | 2025-01-01 |

**컬럼 옵션**

| 옵션 | 의미 |
|------|------|
| `primary_key=True` | 행을 구분하는 고유 번호 (필수 1개) |
| `nullable=False` | 비워둘 수 없음 (필수 항목) |
| `nullable=True` | 비워도 됨 (선택 항목) |
| `unique=True` | 중복 값 불가 |
| `default=값` | 기본값 설정 |

---

### Step 3 - Flask 앱 설정

```python
app = Flask(__name__)

app.config['SECRET_KEY'] = 'my-secret-key'
# ↑ 보안을 위한 비밀 키 (세션, 쿠키 암호화에 사용)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
# ↑ 어떤 DB를 쓸지 주소 지정
#   sqlite:///파일명.db → 파일 하나짜리 간단한 DB (개발할 때 주로 사용)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# ↑ 불필요한 경고 메시지 끄기
```

**DB URI 형식**

```
sqlite:///파일명.db          # SQLite (파일 DB, 설치 불필요)
mysql://user:pw@host/dbname  # MySQL
postgresql://user:pw@host/db # PostgreSQL
```

---

### Step 4 - db와 Flask 앱 연결

```python
db.init_app(app)
```

> 이제 비어있던 SQLAlchemy가 우리 Flask 앱과 연결됨.

---

### Step 5 - 실제 테이블 생성 & 초기 데이터 넣기

```python
if __name__ == '__main__':
    with app.app_context():      # ← Flask 앱 컨텍스트 안에서 실행
        db.create_all()          # ← 모델 클래스를 보고 테이블 자동 생성
        
        if not User.query.first():   # 데이터가 아무것도 없을 때만
            user1 = User(name="user1", age=30)
            db.session.add(user1)    # 추가 예약
            db.session.commit()      # 실제로 저장 (엑셀의 Ctrl+S)
```

> `app_context()` 란?
> Flask는 앱이 여러 개일 수 있어서, "지금 이 앱을 사용한다"고 알려줘야 함.
> `with app.app_context():` 블록 안에서 DB 작업을 해야 에러가 안 남.

---

## 5. CRUD - 데이터 다루기 4가지 기본 동작

> CRUD = **C**reate(추가) / **R**ead(조회) / **U**pdate(수정) / **D**elete(삭제)

### C - 데이터 추가 (Create)

```python
new_user = User(name="김철수", age=25)
db.session.add(new_user)
db.session.commit()
```

---

### R - 데이터 조회 (Read)

```python
# 전체 조회
users = User.query.all()           # 리스트로 반환

# 첫 번째 1개만
user = User.query.first()

# id로 1개 찾기
user = User.query.get(1)           # id=1인 사람

# 조건으로 찾기
users = User.query.filter_by(name="김철수").all()
users = User.query.filter(User.age > 20).all()

# 정렬
users = User.query.order_by(User.age).all()        # 오름차순
users = User.query.order_by(User.age.desc()).all() # 내림차순

# 개수 세기
count = User.query.count()
```

---

### U - 데이터 수정 (Update)

```python
user = User.query.get(1)   # 수정할 사람 찾기
user.age = 31              # 값 변경
db.session.commit()        # 저장
```

---

### D - 데이터 삭제 (Delete)

```python
user = User.query.get(1)   # 삭제할 사람 찾기
db.session.delete(user)    # 삭제 예약
db.session.commit()        # 실제 삭제
```

---

## 6. `__repr__` 메서드란?

```python
def __repr__(self):
    return f'<User {self.id}, {self.name}, {self.age}>'
```

**왜 쓰나요?**
`print(user)` 했을 때 보기 좋게 출력하기 위해서입니다.

```python
# __repr__ 없을 때
print(user)  →  <User object at 0x10f3a2b50>  # 알아볼 수 없음

# __repr__ 있을 때
print(user)  →  <User 1, 홍길동, 30>  # 바로 이해 가능
```

---

## 7. `db.session` 이해하기

> session = **임시 저장 공간** (장바구니 같은 것)

```
add()     →  장바구니에 담기
delete()  →  장바구니에서 제거 표시
commit()  →  결제 완료 (DB에 실제 반영)
rollback() → 장바구니 초기화 (에러 시 되돌리기)
```

---

## 8. 전체 흐름 요약

```
① 모델 정의 (class User)
        ↓
② 앱 설정 (app.config)
        ↓
③ 연결 (db.init_app)
        ↓
④ 테이블 생성 (db.create_all)
        ↓
⑤ 데이터 CRUD (query / session)
        ↓
⑥ HTML에 데이터 전달 (render_template)
```

---

## 9. 자주 하는 실수

| 실수 | 해결 방법 |
|------|-----------|
| `RuntimeError: No application found` | `with app.app_context():` 안에서 DB 작업 |
| 수정했는데 DB에 반영 안 됨 | `db.session.commit()` 빠뜨린 것 |
| 테이블이 안 생김 | `db.create_all()` 실행 필요 |
| 모델 변경 후 반영 안 됨 | DB 파일 삭제 후 재시작 (또는 마이그레이션 사용) |

---

## 10. 핵심 한 줄 요약

```
모델(클래스) = 테이블 구조 정의
db.create_all() = 테이블 생성
db.session.add() + commit() = 데이터 추가/수정/삭제
User.query.xxx = 데이터 조회
```
