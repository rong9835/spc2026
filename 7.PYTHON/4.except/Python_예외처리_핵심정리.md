# Python 예외처리 (Exception Handling) 핵심 정리

## 예외처리란?

> 프로그램 실행 중 **오류(에러)가 발생해도 프로그램이 멈추지 않고** 계속 실행되도록 하는 방법

---

## 기본 구조

```python
try:
    # 오류가 발생할 수 있는 코드
except 오류종류:
    # 오류 발생 시 실행할 코드
```

---

## 자주 쓰는 예외 종류

| 예외 이름 | 발생 상황 | 예시 |
|-----------|-----------|------|
| `ZeroDivisionError` | 0으로 나눌 때 | `10 / 0` |
| `ValueError` | 잘못된 값 변환 시 | `int("hello")` |
| `IndexError` | 리스트 범위 초과 | `list[99]` |
| `FileNotFoundError` | 파일이 없을 때 | `open("없는파일.txt")` |

---

## 예제로 보는 예외처리

### 1. ZeroDivisionError - 0으로 나누기

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print('0으로 나눌 수 없습니다.')
```

```
출력: 0으로 나눌 수 없습니다.
```

---

### 2. ValueError - 잘못된 타입 변환

```python
try:
    number = int("hello")
except ValueError:
    print("해당 글자는 숫자로 변환할 수 없습니다.")
```

```
출력: 해당 글자는 숫자로 변환할 수 없습니다.
```

---

### 3. IndexError - 리스트 범위 초과

```python
alist = [1, 2, 3]
try:
    alist[3]           # 인덱스는 0, 1, 2 까지만 존재
except IndexError:
    print("입력 범위를 초과하였습니다.")
```

```
출력: 입력 범위를 초과하였습니다.
```

---

### 4. FileNotFoundError - 파일 없음

```python
try:
    with open("없는파일명.txt", "r") as file:
        data = file.read()
except FileNotFoundError:
    print("해당 파일이 존재하지 않습니다.")
```

```
출력: 해당 파일이 존재하지 않습니다.
```

---

## 여러 예외 한번에 처리하기

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("0으로 나눌 수 없습니다.")
except:                        # ← 나머지 모든 오류 처리
    print("알 수 없는 오류입니다.")
```

> `except:` (예외 종류 없음) → **모든 예외**를 잡아냄 (마지막에 사용)

---

## 흐름 정리

```
프로그램 실행
    ↓
try 블록 실행
    ↓
오류 발생? ──Yes──→ except 블록 실행 → 계속 진행
    ↓ No
정상 진행
```

---

## 핵심 요약 한 줄

- **try** : 실행해볼 코드
- **except** : 오류 났을 때 대신 실행할 코드
- 예외 종류를 명시하면 → 해당 오류만 처리
- `except:` 만 쓰면 → 모든 오류 처리 (와일드카드)
