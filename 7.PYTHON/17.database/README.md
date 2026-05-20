# 17. 데이터베이스 (SQLite) 핵심 요약

## 데이터베이스가 뭐야?

> 데이터를 **영구적으로 저장**하는 창고

- 변수나 리스트는 프로그램이 꺼지면 사라짐
- 데이터베이스는 파일로 저장되기 때문에 껐다 켜도 유지됨
- 오늘 배운 **SQLite** = 파일 하나(`example.db`)가 통째로 데이터베이스

```
일반 변수     →  RAM (전기 끊기면 사라짐)
데이터베이스  →  HDD (파일로 남음)
```

---

## 핵심 개념 2가지

### 1. `conn` (커넥션) = 데이터베이스 문을 여는 것
```python
conn = sqlite3.connect('example.db')
```
> 마치 도서관 문을 여는 것. 파일이 없으면 자동으로 새로 만들어줌.

### 2. `cur` (커서) = 실제로 작업하는 손
```python
cur = conn.cursor()
```
> 문은 열었으니, 이제 책을 가져오거나 넣어줄 손(커서)을 꺼내는 것.

### 작업 순서 (항상 이 순서!)
```
1. conn = 연결 열기
2. cur = 커서 만들기
3. cur.execute() = SQL 명령 실행
4. conn.commit() = 저장 확정 (변경사항이 있을 때)
5. conn.close() = 연결 닫기
```

---

## 테이블이 뭐야?

> 엑셀 표라고 생각하면 됨

| id | name  | age |
|----|-------|-----|
| 1  | Alice | 30  |
| 2  | Bob   | 25  |

- **테이블** = 표 전체
- **컬럼** = 세로줄 (id, name, age)
- **행(row)** = 가로줄 (한 사람의 데이터)

---

## CRUD - 데이터베이스의 4가지 기본 동작

> **C**reate(만들기) / **R**ead(읽기) / **U**pdate(수정) / **D**elete(삭제)

---

### 1. CREATE - 테이블 만들기 (`1.create.py`)

```python
cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id   INTEGER PRIMARY KEY,   -- 자동 번호표
        name TEXT    NOT NULL,      -- 문자열, 비워두면 안됨
        age  INTEGER NOT NULL       -- 정수, 비워두면 안됨
    )
""")
conn.commit()
```

- `IF NOT EXISTS` = 테이블이 이미 있으면 넘어감 (오류 방지)
- `PRIMARY KEY` = 각 행의 고유 번호 (자동으로 1, 2, 3... 올라감)
- `NOT NULL` = 값이 반드시 있어야 함

---

### 2. INSERT - 데이터 넣기 (`2.insert.py`)

```python
# 안전한 방법 (권장) - ?에 값을 따로 전달
cur.execute('''
    INSERT INTO users (name, age) VALUES (?, ?)
''', ('Alice', 30))

conn.commit()
```

> `?` 를 쓰는 이유: SQL 인젝션(해킹) 방지! 값을 직접 문자열로 붙이면 위험함.

#### 데이터 중복 방지 (`2.insert_if_not_exists.py`)

```python
cur.execute('SELECT COUNT(*) FROM users')
count = cur.fetchone()[0]   # 현재 행 개수

if count == 0:
    # 비어있을 때만 넣기
    cur.execute('INSERT INTO users (name, age) VALUES (?, ?)', ('Alice', 30))
    conn.commit()
else:
    print("이미 데이터가 있습니다.")
```

---

### 3. SELECT - 데이터 읽기 (`3.select.py`)

```python
cur.execute('SELECT * FROM users')   # *  = 모든 컬럼
rows = cur.fetchall()                # 결과를 리스트로 가져오기
print(rows)
# [(1, 'Alice', 30), (2, 'Bob', 25)]
```

| 메서드 | 설명 |
|--------|------|
| `fetchall()` | 결과 전부 리스트로 가져오기 |
| `fetchone()` | 결과 딱 1개만 가져오기 |

---

### 4. UPDATE - 데이터 수정 (`4.update.py`)

```python
cur.execute('''
    UPDATE users SET age=? WHERE name=?
''', (33, 'Bob'))

conn.commit()
```

> `WHERE` 빠뜨리면 **모든 행**이 다 바뀌니 조심!

---

### 5. DELETE - 데이터 삭제 (`5.delete.py`)

```python
cur.execute('''
    DELETE FROM users WHERE name=?
''', ('Bob',))   # 튜플이라서 쉼표 꼭 필요!

conn.commit()
```

> 마찬가지로 `WHERE` 없으면 테이블 전체 삭제됨.

---

### 6. DROP - 테이블 자체를 날리기 (`6.drop.py`)

```python
cur.execute("DROP TABLE users")
conn.commit()
```

> DELETE는 데이터를 지우는 것, DROP은 테이블 구조째로 다 지우는 것

---

## 함수로 정리하기 (`10.total.py`)

반복되는 연결/해제 코드를 함수로 묶으면 훨씬 깔끔해짐.

```python
def connect_db():
    conn = sqlite3.connect('example.db')
    cur = conn.cursor()
    return conn, cur

def disconnect_db(conn):
    conn.commit()
    conn.close()

def insert_user(name, age):
    conn, cur = connect_db()
    cur.execute('INSERT INTO users (name, age) VALUES (?, ?)', (name, age))
    disconnect_db(conn)

def get_users():
    conn, cur = connect_db()
    cur.execute('SELECT * FROM users')
    rows = cur.fetchall()
    disconnect_db(conn)
    return rows

def get_user_by_name(name):
    conn, cur = connect_db()
    cur.execute('SELECT * FROM users WHERE name=?', (name,))
    user = cur.fetchone()   # 한 명만
    disconnect_db(conn)
    return user
```

---

## 라이브러리로 분리하기 (`11.total_refactor.py`)

코드가 길어지면 파일을 나눠서 관리.

```
17.database/
├── database/
│   └── my_crud_lib.py    ← 함수들을 여기에 모아두기
└── 11.total_refactor.py  ← 여기서 가져다 쓰기
```

```python
# 11.total_refactor.py
import database.my_crud_lib as db   # 라이브러리 불러오기

db.create_table()
db.insert_user('Alice', 30)

users = db.get_users()
for user in users:
    print(user)
```

> 마치 `import math` 하고 `math.sqrt()` 쓰는 것처럼, 내가 만든 함수도 모듈로 분리할 수 있음!

---

## 전체 흐름 한눈에 보기

```
파이썬 코드
    ↓  sqlite3.connect()
데이터베이스 연결 (conn)
    ↓  conn.cursor()
커서 생성 (cur)
    ↓  cur.execute("SQL 명령")
SQL 실행
    ↓  conn.commit()   ← 변경사항 있을 때만
저장 확정
    ↓  conn.close()
연결 종료
```

---

## 자주 쓰는 SQL 명령 요약

| 동작 | SQL |
|------|-----|
| 테이블 만들기 | `CREATE TABLE IF NOT EXISTS 테이블명 (...)` |
| 데이터 넣기 | `INSERT INTO 테이블명 (컬럼) VALUES (?)` |
| 데이터 읽기 | `SELECT * FROM 테이블명` |
| 조건 검색 | `SELECT * FROM 테이블명 WHERE 컬럼=?` |
| 데이터 수정 | `UPDATE 테이블명 SET 컬럼=? WHERE 조건=?` |
| 데이터 삭제 | `DELETE FROM 테이블명 WHERE 조건=?` |
| 테이블 삭제 | `DROP TABLE 테이블명` |
| 개수 세기 | `SELECT COUNT(*) FROM 테이블명` |
