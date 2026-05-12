# Python 기초 핵심 정리

---

## 1. 출력 (print)

```python
print("Hello")              # 기본 출력
print("Hello", "Python")    # 여러 값 출력 (공백으로 연결)
print("Hello" + "Python")   # 문자열 연결

# 문자열 포맷팅 (3가지 방법)
name = "홍길동"
num = 5

print("Hello, {}".format(name))           # format()
print("Hello, %s" % name)                 # % 포맷
print(f"Hello, {name}. 번호는 {num}")     # f-string (가장 많이 씀!)

# 줄바꿈 제어
print("텍스트", end="")    # 줄바꿈 없이
print("텍스트", end="\n")  # 줄바꿈 (기본값)

# 멀티라인 문자열
text = """
여러 줄에 걸친
문자열 입력 가능
"""
```

---

## 2. 반복 패턴 (for + 문자열 연산)

```python
# 문자열 반복
print("*" * 5)     # *****
print("=" * 30)    # ============================

# for + range
for i in range(1, 6):    # 1, 2, 3, 4, 5  (6은 미포함)
    print("*" * i)

# 삼각형 패턴
for i in range(1, 6):
    print(" " * (5 - i) + "*" * (2*i - 1))
```

---

## 3. 숫자 (int / float)

```python
# 4칙 연산
x, y = 5, 3
print(x + y)   # 8
print(x - y)   # 2
print(x * y)   # 15
print(x / y)   # 1.666...

# 특수 연산
print(x % y)   # 2     (나머지)
print(x ** y)  # 125   (제곱: ^ 아님!)

# 진법 변환
print(bin(11))  # 0b1011  (2진수)
print(hex(11))  # 0xb     (16진수) ← 자주 씀

# 유용한 함수들
print(abs(-10))   # 10    (절대값)
print(int(4.5))   # 4     (소수점 버림)
print(int("100")) # 100   (문자열 → 숫자)

# 비트 연산
print(5 & 3)   # 1   (AND)
print(5 | 3)   # 7   (OR)
print(5 << 1)  # 10  (왼쪽 시프트 = ×2)
print(5 >> 1)  # 2   (오른쪽 시프트 = ÷2)
```

---

## 4. 문자열 (string)

```python
s = "Hello, World"

# 대소문자
s.lower()       # hello, world
s.upper()       # HELLO, WORLD
s.capitalize()  # Hello, world  (첫 문장만 대문자)
s.title()       # Hello, World  (각 단어 대문자)

# 공백 제거
s.strip()   # 앞뒤 공백 제거
s.lstrip()  # 왼쪽만
s.rstrip()  # 오른쪽만

# 분할 / 합치기
s = "apple,banana,cherry"
parts = s.split(",")          # ['apple', 'banana', 'cherry']
",".join(parts)               # 'apple,banana,cherry'  (다시 합치기)

# 검색
s.startswith("Hello")  # True
s.endswith("World")    # True
s.find("World")        # 7   (위치 반환, 없으면 -1)
```

---

## 5. 리스트 (list)

> 순서 있고, 수정 가능한 자료구조

```python
my_list = [1, 2, 3, 4, 5]

# 인덱싱
my_list[0]   # 1  (첫 번째)
my_list[-1]  # 5  (마지막)

# 슬라이싱 [start:end]  → end는 미포함
my_list[1:3]  # [2, 3]
my_list[:2]   # [1, 2]
my_list[2:]   # [3, 4, 5]

# 추가 / 삭제
my_list.append(6)      # 끝에 추가
my_list.insert(2, 99)  # [2] 위치에 삽입
my_list.remove(99)     # 값으로 삭제
my_list.pop(3)         # 인덱스로 삭제 (값 반환)
my_list.pop()          # 맨 뒤 삭제
my_list.clear()        # 전체 비우기

# 정렬
my_list.sort()                    # 원본 변경
new_list = sorted(my_list)        # 원본 유지, 복사본 반환
my_list.sort(reverse=True)        # 내림차순

# 복사
copy = my_list.copy()

# 리스트 합산
[1,2,3] + [4,5,6]  # [1, 2, 3, 4, 5, 6]
[1,2,3] * 3        # [1, 2, 3, 1, 2, 3, 1, 2, 3]
```

### 리스트 컴프리헨션 (한 줄로 리스트 만들기)

```python
numbers = [x for x in range(1, 10)]           # [1~9]
squares = [x**2 for x in range(5)]            # [0,1,4,9,16]
evens   = [x for x in range(1,10) if x%2==0] # 짝수만
odds    = [x for x in range(1,10) if x%2==1] # 홀수만
```

---

## 6. 튜플 (tuple)

> 리스트와 동일하지만 **읽기 전용** (수정 불가)

```python
my_tuple = (1, 2, 3, 4, 5)

my_tuple[2]     # 3  (읽기 OK)
# my_tuple[2] = 99   # ERROR! 수정 불가

# 수정이 필요하면 → 리스트로 변환
my_list = list(my_tuple)
my_list[2] = 99
my_tuple2 = tuple(my_list)  # 다시 튜플로

# 튜플 언패킹 (자주 씀!)
a, b, c = (1, 2, 3)

person = ("홍길동", 25, "학생")
name, age, job = person
```

---

## 7. 딕셔너리 (dict)

> `키: 값` 쌍으로 이루어진 자료구조. JSON과 유사

```python
my_dict = {"name": "Alice", "age": 25}

# 읽기
my_dict["name"]   # Alice

# 추가
my_dict["car"] = "BMW"

# 삭제
del my_dict["age"]          # del 키워드
my_dict.pop("age")          # pop (삭제하면서 값 반환)
my_dict.clear()             # 전체 삭제

# 딕셔너리 컴프리헨션
squares = {x: x**2 for x in range(5)}  # {0:0, 1:1, 2:4, ...}

# 키/값 목록
my_dict.keys()    # 키 목록
my_dict.values()  # 값 목록
my_dict.items()   # (키, 값) 쌍 목록 ← for문에서 자주 씀
```

---

## 8. 조건문 (if / elif / else)

```python
score = 65

if score >= 80:
    grade = 'A'
elif score >= 70:
    grade = 'B'
elif score >= 60:
    grade = 'C'
else:
    grade = 'F'

print(f"점수: {score}, 학점: {grade}")

# in 연산자로 목록 비교
month = 7
if month in [6, 7, 8]:
    season = "여름"

# 복합 조건
if username and password:           # 둘 다 값이 있을 때
    if username == 'admin' and password == '1234':
        print("관리자 로그인")
```

---

## 9. 반복문 (for)

```python
numbers = [1, 2, 3, 4, 5]

# 기본 for
for num in numbers:
    if num % 2 == 0:
        print(f"{num} 은 짝수")
    else:
        print(f"{num} 은 홀수")

# 짝수 / 홀수 분리
even, odd = [], []
for num in numbers:
    if num % 2 == 0:
        even.append(num)
    else:
        odd.append(num)

# 딕셔너리 순회
students = {"김민준": 87, "이서연": 92}
for name, score in students.items():
    if score >= 90:
        print(f"{name} → A등급")
```

> **시간복잡도 주의**: 중첩 for가 4단계면 O(n⁴) → 매우 느려짐

---

## 10. 함수 (def)

```python
# 기본 함수
def add_numbers(a, b):
    return a + b

result = add_numbers(3, 4)   # 7

# 여러 값 반환 (튜플로 반환됨)
def calculate_all(a, b):
    return a+b, a-b, a*b, a/b

add, sub, mul, div = calculate_all(3, 4)

# 필요한 값만 받기 (나머지는 _ 로 무시)
add, _, mul, _ = calculate_all(5, 6)

# 기본값(default) 파라미터
def create_profile(name, age, city="서울", job="학생"):
    return f"이름: {name}, 나이: {age}, 지역: {city}, 직업: {job}"

create_profile("홍길동", 23)            # 기본값 사용
create_profile("이길동", 27, "부산")    # city만 변경

# 키워드 인자 (순서 상관없이 전달)
create_profile(age=25, name="박길동")
```

---

## 11. 실전 예제 - 사용자 검색

```python
users = [
    {"name": "김민준", "age": 25, "location": "서울"},
    {"name": "이서연", "age": 31, "location": "부산"},
    ...
]

# 이름 앞글자(성)로 검색
def find_user(name):
    for user in users:
        if user["name"].startswith(name):
            print(user)

find_user("김")

# 다중 조건 검색 (깔끔한 방법)
def find_users(name=None, age=None, location=None):
    found = []
    for user in users:
        if (name is None or user["name"] == name) and \
           (age is None or user["age"] == age) and \
           (location is None or user["location"] == location):
            found.append(user)
    return found

find_users(age=25)                        # 나이만
find_users("김민준", 25, "서울")          # 전부
```

---

## 핵심 요약 표

| 자료구조 | 기호 | 수정 | 특징 |
|---------|------|------|------|
| 리스트 | `[ ]` | O | 순서 있음, 범용적 |
| 튜플 | `( )` | X | 읽기 전용, 언패킹 유용 |
| 딕셔너리 | `{ }` | O | 키:값 쌍, JSON 유사 |

| 개념 | 핵심 문법 |
|------|---------|
| f-string | `f"값: {변수}"` |
| 슬라이싱 | `list[start:end]` (end 미포함) |
| 컴프리헨션 | `[x for x in range(n) if 조건]` |
| 언패킹 | `a, b, c = (1, 2, 3)` |
| 기본값 파라미터 | `def f(x, y="기본값"):` |
| 다중 반환 | `return a, b, c` |
