# Python 클래스(Class) 핵심 정리

---

## 1. 클래스란?

> 객체(Object)를 만들기 위한 **설계도(틀)**

- **클래스** → 설계도 (붕어빵 틀)
- **인스턴스(객체)** → 실제 만들어진 것 (붕어빵)

```python
class Person:           # 클래스 정의
    ...

person1 = Person(...)   # 인스턴스(객체) 생성
```

---

## 2. 클래스 기본 구조

```python
class Person:
    def __init__(self, name, age):   # 생성자: 객체 생성 시 자동 호출
        self.name = name             # 인스턴스 변수 (속성)
        self.age = age

    def greet(self):                 # 메서드 (함수)
        print(f"안녕하세요, 저는 {self.name} 입니다.")
```

| 요소 | 설명 |
|------|------|
| `__init__` | 생성자. 객체 만들 때 자동 실행 |
| `self` | 자기 자신(인스턴스)을 가리키는 참조 |
| `self.변수명` | 인스턴스 변수 (속성) |
| `def 메서드명(self)` | 인스턴스 메서드 |

---

## 3. 객체 생성 & 사용

```python
person1 = Person("Alice", 25)   # 객체 생성
person2 = Person("Bob", 27)

person1.greet()          # 메서드 호출 → "안녕하세요, 저는 Alice 입니다."
person1.study("Python")  # 인자 전달도 가능
```

---

## 4. getter / setter 패턴

> 속성을 **읽고 / 쓰는** 전용 메서드

```python
class Person:
    def get_name(self):          # getter: 값 읽기
        return self.name

    def get_age(self):
        return self.age

    def set_age(self, value):    # setter: 값 변경
        self.age = value
```

```python
person = Person("Bob", 30)
person.set_age(40)               # 나이 변경
print(person.get_name())         # "Bob" 출력
```

---

## 5. 상속 (Inheritance)

> 부모 클래스의 속성과 메서드를 **그대로 물려받아** 재사용

```
Person (부모)
├── Employee (자식) - 회사 정보 추가
└── Driver   (자식) - 자동차 정보 추가
```

```python
class Employee(Person):              # Person을 상속
    def __init__(self, name, age, company):
        super().__init__(name, age)  # 부모 생성자 호출
        self.company = company       # 추가 속성
```

- `super()` → 부모 클래스를 가리킴
- 부모의 `__init__`을 먼저 실행 후 자식 속성 추가

---

## 6. 메서드 오버라이딩 (Override)

> 부모에게 물려받은 메서드를 **자식이 재정의**

```python
# 부모 Person의 greet
def greet(self):
    print(f"안녕하세요, 저는 {self.age}살 {self.name} 입니다.")

# 자식 Employee의 greet (오버라이딩)
def greet(self):
    print(f"안녕하세요, 저는 {self.company} 에 다니고 있는 {self.name} 입니다.")
```

같은 메서드 이름이지만 **동작이 달라짐** → 다형성(Polymorphism)

---

## 7. 전체 구조 예시 (company 폴더)

```
person.py   → Person 클래스 (부모)
employee.py → Employee 클래스 (Person 상속)
driver.py   → Driver 클래스 (Person 상속)
main.py     → 각 클래스 임포트 후 사용
```

```python
# main.py
from employee import Employee
from person import Person
from driver import Driver

employee1 = Employee("James", 25, "Samsung")
employee1.greet()   # Employee의 greet 실행

employee3 = Person("Bob", 30)
employee3.set_age(40)   # setter로 나이 변경
employee3.greet()       # 변경된 나이로 출력

employee4 = Driver("홍길동", 40, "BMW")
employee4.greet()         # Person의 greet (오버라이딩 없음)
employee4.drive()         # Driver 고유 메서드
employee4.drive_fast()    # Driver 고유 메서드
```

---

## 8. 핵심 개념 한눈에 보기

```
클래스(Class)
│
├── __init__(self, ...)    → 생성자 (객체 초기화)
├── self.속성              → 인스턴스 변수
├── def 메서드(self)       → 인스턴스 메서드
│
└── 상속(Inheritance)
    ├── class 자식(부모)   → 부모 클래스 상속
    ├── super().__init__() → 부모 생성자 호출
    └── 오버라이딩         → 부모 메서드 재정의
```

| 개념 | 키워드 | 설명 |
|------|--------|------|
| 클래스 정의 | `class 이름:` | 설계도 작성 |
| 생성자 | `__init__` | 객체 생성 시 자동 실행 |
| 자기 참조 | `self` | 자기 자신 인스턴스 |
| 상속 | `class 자식(부모)` | 부모 기능 물려받기 |
| 부모 호출 | `super()` | 부모 클래스 접근 |
| 오버라이딩 | 같은 이름 재정의 | 동작 변경 |
| getter | `get_변수명()` | 속성 읽기 메서드 |
| setter | `set_변수명()` | 속성 쓰기 메서드 |
