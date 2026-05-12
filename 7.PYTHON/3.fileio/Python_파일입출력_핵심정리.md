# Python 파일 입출력 핵심정리

---

## 목차
1. [파일 열기 기본 개념](#1-파일-열기-기본-개념)
2. [텍스트 파일 쓰기](#2-텍스트-파일-쓰기)
3. [텍스트 파일 읽기](#3-텍스트-파일-읽기)
4. [CSV 파일 쓰기](#4-csv-파일-쓰기)
5. [CSV 파일 읽기](#5-csv-파일-읽기)
6. [전체 흐름 한눈에 보기](#6-전체-흐름-한눈에-보기)

---

## 1. 파일 열기 기본 개념

### `open()` 함수

```python
open("파일명", "모드", encoding="utf-8")
```

| 모드 | 의미 | 파일 없으면? |
|------|------|-------------|
| `"w"` | 쓰기 (덮어씀) | 새로 생성 |
| `"r"` | 읽기 | 오류 발생 |
| `"a"` | 추가 쓰기 | 새로 생성 |

### `with` 문 사용 (권장)

```python
# 권장 방식 — 자동으로 파일을 닫아줌
with open("file.txt", "r", encoding="utf-8") as file:
    data = file.read()

# 구식 방식 — 직접 close() 해야 함
file = open("file.txt", "r", encoding="utf-8")
data = file.read()
file.close()  # 깜빡하면 파일이 잠긴 채로 남음
```

> `with` 문을 쓰면 블록이 끝날 때 자동으로 `file.close()`가 호출됩니다.

---

## 2. 텍스트 파일 쓰기

```python
with open("file.txt", "w", encoding="utf-8") as file:
    file.write("한글 테스트 \n")         # \n 으로 줄바꿈
    file.write("Hello, World Again 333")
```

**결과 (`file.txt`):**
```
한글 테스트 
Hello, World Again 333
```

> - `"w"` 모드는 기존 내용을 **완전히 덮어씁니다.**
> - 한글이 포함되면 반드시 `encoding="utf-8"` 지정!

---

## 3. 텍스트 파일 읽기

### 방법 1 — 전체 읽기 (작은 파일용)

```python
with open("file.txt", "r", encoding="utf-8") as file:
    data = file.read()     # 파일 전체를 문자열 하나로 읽음
    print(data)
```

### 방법 2 — 줄 단위 읽기 (큰 파일용)

```python
with open("file.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()    # 각 줄을 리스트로 반환

    for line in lines:
        print(line)
```

| 메서드 | 반환 타입 | 언제 사용? |
|--------|-----------|-----------|
| `file.read()` | `str` (전체 문자열) | 파일이 작을 때 |
| `file.readlines()` | `list` (줄별 리스트) | 파일이 크거나 줄 단위 처리 시 |

---

## 4. CSV 파일 쓰기

> CSV = **Comma Separated Values** — 쉼표로 구분된 표 형태 파일

```python
import csv
```

### 방법 1 — 리스트 방식 (구식)

```python
data = [
    ["Name", "Age", "City"],   # 첫 번째 줄 = 헤더
    ["John", 25, "Seoul"],
    ["James", 23, "Busan"],
]

with open("data.csv", "w", newline="") as file:
    csv_writer = csv.writer(file)
    csv_writer.writerows(data)   # 리스트 전체를 한번에 씀
```

### 방법 2 — 딕셔너리 방식 (모던, 권장)

```python
data = [
    {"Name": "John",  "Age": 25, "City": "Seoul"},
    {"Name": "James", "Age": 23, "City": "Busan"},
    {"Name": "Bob",   "Age": 24, "City": "Seoul"},
]

with open("data.csv", "w", newline="") as file:
    headers = data[0].keys()                         # 헤더 자동 추출
    csv_writer = csv.DictWriter(file, fieldnames=headers)
    csv_writer.writeheader()    # 첫줄에 헤더 작성
    csv_writer.writerows(data)  # 딕셔너리 리스트 전체 저장
```

**결과 (`data.csv`):**
```
Name,Age,City
John,25,Seoul
James,23,Busan
Bob,24,Seoul
```

> `newline=""` 를 빠뜨리면 Windows에서 빈 줄이 생깁니다.

---

## 5. CSV 파일 읽기

### 방법 1 — 리스트로 읽기

```python
data = []
with open("data.csv", "r") as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        data.append(row)

print(data)
# [['Name', 'Age', 'City'], ['John', '25', 'Seoul'], ...]
```

### 방법 2 — 딕셔너리로 읽기 (모던, 권장)

```python
data = []
with open("data.csv", "r") as file:
    csv_reader = csv.DictReader(file)   # 첫줄을 자동으로 헤더로 사용
    for row in csv_reader:
        data.append(row)

print(data)
# [{'Name': 'John', 'Age': '25', 'City': 'Seoul'}, ...]
```

| | `csv.reader` | `csv.DictReader` |
|--|---|---|
| 반환 형태 | `['John', '25', 'Seoul']` | `{'Name': 'John', 'Age': '25'}` |
| 헤더 처리 | 헤더도 데이터로 포함 | 헤더를 키로 자동 처리 |
| 접근 방법 | `row[0]`, `row[1]` | `row['Name']`, `row['Age']` |
| 가독성 | 낮음 | 높음 (권장) |

---

## 6. 전체 흐름 한눈에 보기

```
[ 텍스트 파일 ]

  쓰기: open("file.txt", "w") → file.write("내용")
  읽기: open("file.txt", "r") → file.read() / file.readlines()


[ CSV 파일 ]

  쓰기 (리스트):  csv.writer    → writerows(리스트)
  쓰기 (딕셔너리): csv.DictWriter → writeheader() + writerows(딕셔너리)

  읽기 (리스트):  csv.reader    → for row in reader
  읽기 (딕셔너리): csv.DictReader → for row in reader (row['컬럼명']으로 접근)
```

### 핵심 요약 표

| 작업 | 클래스/함수 | 특징 |
|------|------------|------|
| 텍스트 쓰기 | `open("w")` + `file.write()` | `encoding="utf-8"` 필수 (한글 포함 시) |
| 텍스트 읽기 전체 | `file.read()` | 문자열 반환 |
| 텍스트 읽기 줄단위 | `file.readlines()` | 리스트 반환 |
| CSV 쓰기 (리스트) | `csv.writer` | 헤더 직접 포함해야 함 |
| CSV 쓰기 (딕셔너리) | `csv.DictWriter` | 헤더 자동 관리 |
| CSV 읽기 (리스트) | `csv.reader` | 인덱스로 접근 |
| CSV 읽기 (딕셔너리) | `csv.DictReader` | 컬럼명으로 접근 (권장) |
