# SQLAlchemy 핵심 정리

> Python에서 데이터베이스를 **파이썬 코드로** 다루게 해주는 라이브러리

---

## SQLAlchemy란?

- SQL을 직접 쓰는 대신 **파이썬 클래스/객체**로 DB를 조작하는 도구
- 이런 방식을 **ORM (Object Relational Mapping)** 이라고 부름
- 비유: "DB 테이블 = 파이썬 클래스", "DB 행(row) = 파이썬 객체"

```
일반 SQL:  INSERT INTO users (name, age) VALUES ('홍길동', 25)
SQLAlchemy: session.add(User(name="홍길동", age=25))
```

---

## 설치

```bash
pip install sqlalchemy
```

---

## 핵심 구성요소 4가지

| 구성요소 | 역할 | 비유 |
|---------|------|------|
| `engine` | DB에 연결하는 통로 | 데이터베이스로 가는 도로 |
| `Base` | 테이블 설계의 기반 | 건물 짓기 전 땅 |
| `Model(클래스)` | 테이블 구조 정의 | 건물 설계도 |
| `session` | 실제 작업(CRUD)을 처리 | 건물 안에서 일하는 사람 |

---

## 1단계: 연결 (Engine)

```python
from sqlalchemy import create_engine

# SQLite (파일 기반, 개발용으로 간단)
engine = create_engine('sqlite:///example.db')

# 실제 서비스에서는 PostgreSQL, MySQL 등을 사용
# engine = create_engine('postgresql://user:password@localhost/dbname')
```

---

## 2단계: 테이블 정의 (Model)

```python
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()  # 모든 테이블의 부모 클래스

class User(Base):
    __tablename__ = 'users'          # 실제 DB 테이블 이름

    id = Column(Integer, primary_key=True)  # 고유번호 (자동 증가)
    name = Column(String)                    # 이름
    age = Column(Integer)                    # 나이
```

> 클래스 하나 = 테이블 하나, 클래스 속성 = 컬럼

---

## 3단계: 테이블 생성

```python
Base.metadata.create_all(engine)
# 위 코드 실행 시 DB 파일에 'users' 테이블이 실제로 만들어짐
# 이미 테이블이 있으면 다시 만들지 않음 (안전)
```

---

## 4단계: 세션 열기

```python
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)

# 방법 1: 수동 관리
session = Session()

# 방법 2: with문 (자동으로 닫힘 - 추천)
with Session() as session:
    # 여기서 작업
    pass
```

---

## CRUD 핵심 패턴

### C - Create (추가)

```python
new_user = User(name="홍길동", age=25)
session.add(new_user)
session.commit()  # 저장 확정 (이걸 해야 실제로 저장됨)
```

> `commit()`은 "저장 버튼 누르기"와 같음. 안 하면 반영 안 됨!

---

### R - Read (조회)

```python
# 전체 조회
users = session.query(User).all()

# id로 한 명 조회 (modern 방식)
user = session.get(User, 1)

# 조건으로 조회 (이름이 홍길동인 사람 전체)
users = session.query(User).filter_by(name="홍길동").all()
```

---

### U - Update (수정)

```python
user = session.get(User, 1)    # 1번 사용자 찾기
if user:
    user.age = 30              # 값 변경
    session.commit()           # 저장
```

> 조회 → 수정 → commit() 순서를 꼭 지킬 것

---

### D - Delete (삭제)

```python
user = session.get(User, 1)    # 1번 사용자 찾기
if user:
    session.delete(user)       # 삭제 예약
    session.commit()           # 저장
```

---

## 전체 흐름 요약

```
1. create_engine()      → DB 연결 설정
2. Base + class 정의    → 테이블 구조 설계
3. create_all()         → 실제 테이블 생성
4. Session() 열기       → 작업 준비
5. CRUD 작업            → add / get / query / delete
6. commit()             → 변경사항 저장
```

---

## 자주 쓰는 filter 패턴

```python
# 같다
session.query(User).filter_by(name="홍길동").all()

# 크다/작다 (filter 사용)
from sqlalchemy import and_
session.query(User).filter(User.age > 20).all()

# 여러 조건
session.query(User).filter(User.age > 20, User.name == "홍길동").first()

# 첫 번째 결과만
session.query(User).filter_by(name="홍길동").first()
```

---

## 주의사항

| 실수 | 결과 | 해결 |
|------|------|------|
| `commit()` 빠뜨림 | 변경사항이 저장 안 됨 | 항상 작업 후 `commit()` |
| 없는 id로 `session.get()` | `None` 반환 | `if user:` 로 확인 |
| 테이블 정의 후 `create_all()` 안 함 | 테이블이 만들어지지 않음 | 반드시 `create_all()` 실행 |

---

## 한 눈에 보는 비교

```python
# 일반 SQL 방식
import sqlite3
conn = sqlite3.connect('example.db')
cursor = conn.cursor()
cursor.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("홍길동", 25))
conn.commit()

# SQLAlchemy 방식
session.add(User(name="홍길동", age=25))
session.commit()
```

> SQLAlchemy는 SQL을 직접 쓰지 않아도 되고, 파이썬답게 코드를 작성할 수 있음
