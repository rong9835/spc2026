# Python 모듈 핵심정리

---

## 목차
1. [math — 수학 계산](#1-math--수학-계산)
2. [datetime — 날짜와 시간](#2-datetime--날짜와-시간)
3. [random — 난수 생성](#3-random--난수-생성)
4. [string — 문자열 상수](#4-string--문자열-상수)
5. [os — 운영체제 제어](#5-os--운영체제-제어)
6. [requests — HTTP 요청](#6-requests--http-요청)
7. [BeautifulSoup — HTML 파싱](#7-beautifulsoup--html-파싱)
8. [requests + BeautifulSoup 조합 (웹 스크래핑)](#8-requests--beautifulsoup-조합-웹-스크래핑)

---

## 1. `math` — 수학 계산

> 내장 모듈 (별도 설치 불필요)

```python
import math

math.pi          # 원주율 3.14159...
math.e           # 자연상수 2.71828...
math.sqrt(16)    # 제곱근 → 4.0
math.floor(3.9)  # 내림   → 3
math.sin(0)      # 삼각함수 (라디안 단위)
math.sin(math.pi)
```

| 함수 | 설명 |
|------|------|
| `math.pi` | 원주율 π |
| `math.e` | 자연상수 e |
| `math.sqrt(n)` | 제곱근 |
| `math.floor(n)` | 내림 (소수점 버림) |
| `math.sin(n)` | 사인 (라디안 단위) |

---

## 2. `datetime` — 날짜와 시간

> 내장 모듈 (별도 설치 불필요)

```python
import datetime as dt

# 현재 날짜/시간
dt.datetime.now()                          # 2025-01-01 10:30:00.000

# 포맷 지정 출력
dt.datetime.now().strftime('%Y-%m-%d')     # "2025-01-01"
dt.datetime.now().strftime('%H:%M:%S')     # "10:30:00"

# 특정 날짜 지정
a_day = dt.datetime(2025, 1, 1, 10, 0, 0)  # 연, 월, 일, 시, 분, 초
b_day = dt.datetime(2025, 1, 1)             # 연, 월, 일만
```

| 포맷 코드 | 의미 | 예시 |
|-----------|------|------|
| `%Y` | 4자리 연도 | 2025 |
| `%m` | 월 (01~12) | 01 |
| `%d` | 일 (01~31) | 15 |
| `%H` | 시 (00~23) | 10 |
| `%M` | 분 (00~59) | 30 |
| `%S` | 초 (00~59) | 00 |

---

## 3. `random` — 난수 생성

> 내장 모듈 (별도 설치 불필요)

```python
import random

random.random()           # 0.0 이상 1.0 미만 실수
random.randint(1, 100)    # 1 이상 100 이하 정수 (양 끝 포함)
random.choice(리스트)      # 리스트에서 랜덤 1개 선택
```

### 실전 예시

```python
# 주사위 던지기
def roll_dice():
    return random.randint(1, 6)

# 리스트에서 랜덤 선택
fruits = ['apple', 'banana', 'cherry']
random.choice(fruits)     # 'banana' (매번 다름)

# 랜덤 비밀번호 생성
import string
chars = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
''.join(random.choice(chars) for _ in range(8))
```

| 함수 | 설명 | 범위 |
|------|------|------|
| `random()` | 실수 난수 | 0.0 ≤ x < 1.0 |
| `randint(a, b)` | 정수 난수 | a ≤ x ≤ b |
| `choice(seq)` | 시퀀스에서 1개 선택 | — |

---

## 4. `string` — 문자열 상수

> 내장 모듈 (별도 설치 불필요)

```python
import string

string.ascii_letters   # 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
string.digits          # '0123456789'
string.ascii_lowercase # 'abcdefghijklmnopqrstuvwxyz'
string.ascii_uppercase # 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
```

> 주로 `random`과 함께 사용해 비밀번호, 인증코드 등을 만들 때 활용

---

## 5. `os` — 운영체제 제어

> 내장 모듈 (별도 설치 불필요)

```python
import os

os.getcwd()          # 현재 작업 디렉토리 경로 반환
os.chdir("경로")      # 작업 디렉토리 변경
os.listdir("경로")    # 해당 경로의 파일/폴더 목록 반환
os.mkdir("폴더명")    # 폴더 생성
os.rmdir("폴더명")    # 폴더 삭제
```

```python
# 예시
os.getcwd()                    # '/Users/chorong/spc2026'
os.listdir(os.getcwd())        # ['file1.py', 'folder1', ...]
```

---

## 6. `requests` — HTTP 요청

> 외부 모듈 → **설치 필요**
```bash
pip install requests
```

```python
import requests

# GET 요청
resp = requests.get("https://api.github.com")

# 응답 확인
resp.status_code   # 200 (성공), 404 (없음), 500 (서버오류) 등
resp.text          # HTML 또는 JSON 텍스트

# 상태 코드로 성공 여부 체크
if resp.status_code == 200:
    print(resp.text)
else:
    print("실패 코드:", resp.status_code)
```

### HTML에서 태그 찾기 (수동 파싱)

```python
html = response.text

start = html.find("<h1>")    # <h1> 시작 위치
end   = html.find("</h1>")   # </h1> 위치

text = html[start+4:end]     # 태그 안의 텍스트만 추출
```

> 수동 파싱은 복잡 → BeautifulSoup으로 더 쉽게 처리 가능

---

## 7. `BeautifulSoup` — HTML 파싱

> 외부 모듈 → **설치 필요**
```bash
pip install bs4
```

```python
from bs4 import BeautifulSoup

html = """
<html>
  <body>
    <h1>Title</h1>
    <p>첫번째 단락</p>
    <p>두번째 단락</p>
  </body>
</html>
"""

soup = BeautifulSoup(html, "html.parser")

soup.find("h1")          # 첫번째 h1 태그 1개 반환
soup.find_all("p")       # 모든 p 태그 리스트 반환
```

| 메서드 | 설명 |
|--------|------|
| `find("태그")` | 조건에 맞는 **첫번째** 태그 반환 |
| `find_all("태그")` | 조건에 맞는 **모든** 태그 리스트 반환 |
| `태그.get("속성")` | 태그의 특정 속성값 추출 |
| `태그.text` | 태그 안의 텍스트만 추출 |

---

## 8. `requests` + `BeautifulSoup` 조합 (웹 스크래핑)

> 실제 웹페이지에서 데이터를 가져오는 핵심 패턴

```python
import requests
from bs4 import BeautifulSoup

# 1. 웹페이지 요청
url = "https://www.naver.com"
resp = requests.get(url)

# 2. HTML 파싱
soup = BeautifulSoup(resp.text, "html.parser")

# 3. 원하는 태그 찾기
title    = soup.find("title")      # <title> 태그 1개
headings = soup.find_all("h1")     # 모든 <h1> 태그
divs     = soup.find_all("div")    # 모든 <div> 태그

# 4. 링크 추출 예시
for elem in divs:
    link = elem.a              # div 안의 <a> 태그
    if link:
        href = link.get("href")   # href 속성값 추출
        print("링크:", href)
```

### 웹 스크래핑 흐름 요약

```
URL 주소
  ↓  requests.get(url)
HTML 텍스트 (resp.text)
  ↓  BeautifulSoup(html, "html.parser")
soup 객체
  ↓  find() / find_all()
원하는 태그/데이터 추출
```

---

## 전체 모듈 한눈에 보기

| 모듈 | 설치 | 주요 용도 |
|------|------|-----------|
| `math` | 내장 | 수학 계산 (제곱근, 삼각함수 등) |
| `datetime` | 내장 | 날짜·시간 처리 및 포맷 |
| `random` | 내장 | 난수 생성, 랜덤 선택 |
| `string` | 내장 | 문자열 상수 (알파벳, 숫자 모음) |
| `os` | 내장 | 파일 시스템, 디렉토리 제어 |
| `requests` | `pip install requests` | HTTP GET/POST 요청 |
| `bs4 (BeautifulSoup)` | `pip install bs4` | HTML 파싱 및 데이터 추출 |
