# 파이썬 API 핵심 정리 (왕초보용)

---

## API가 뭐야? 🍽️

> **식당 비유로 이해하기**
>
> - **나 (내 코드)** = 손님
> - **API 서버** = 주방
> - **API 요청** = 주문서
> - **API 응답** = 음식이 나오는 것

"이 데이터 줘!" 하고 요청하면, 서버가 데이터를 돌려주는 것.

---

## API 키가 뭐야? 🔑

> **출입증** 같은 것. "나 허락받은 사람이에요" 라는 증명서.

- YouTube, Gemini, 네이버 같은 API는 **키가 있어야** 사용 가능
- GitHub API는 **키 없이도** 사용 가능 (단, 하루 사용 횟수 제한 있음)

---

## API 키는 어떻게 관리해? 🔒

> **코드에 직접 쓰면 절대 안 됨!**
> 깃허브에 올리면 전 세계 사람이 다 볼 수 있어서 **해킹 위험**!

**방법: `.env` 파일에 따로 보관**

```
# .env 파일 (이 파일은 절대 깃허브에 올리면 안 됨!)
YOUTUBE_API_KEY=여기에내키값
GEMINI_API_KEY=여기에내키값
NAVER_CLIENT_ID=여기에내키값
```

```python
# 코드에서 꺼내 쓰는 법
from dotenv import load_dotenv
import os

load_dotenv()                          # .env 파일 읽기
API_KEY = os.getenv("YOUTUBE_API_KEY") # 키 가져오기
```

> `.gitignore` 파일에 `.env` 추가하면 깃허브에 올라가지 않음!

---

## 1. GitHub API — 키 없이 사용 가능! 🐙

### 특정 유저의 레포 목록 가져오기 (`1.githubapi.py`)

```python
import requests

url = "https://api.github.com/users/아이디/repos"

resp = requests.get(url)   # 요청 보내기
repos = resp.json()        # 받은 데이터를 파이썬 리스트로 변환

for repo in repos:
    print(repo["name"])      # 레포 이름
    print(repo["html_url"])  # 레포 URL
```

### 키워드로 레포 검색하기 (`2.github_search.py`)

```python
url = 'https://api.github.com/search/repositories'

params = {
    'q': 'chatbot',   # 검색어
    'per_page': 100,  # 한 번에 최대 100개
    'page': 1         # 1페이지
}

resp = requests.get(url, params)
data = resp.json()

# 검색 결과는 data['items'] 안에 있음
for repo in data['items']:
    print(repo['name'], repo['html_url'])
```

### 여러 페이지 한꺼번에 모으기 (`3.github_search2.py`)

```python
all_repos = []

for page in range(1, 11):   # 1~10페이지 반복
    params = {'q': 'chatbot', 'per_page': 100, 'page': page}
    resp = requests.get(url, params)
    data = resp.json()

    if 'items' in data:             # 결과가 있을 때만
        all_repos += data['items'] # 리스트에 추가
```

> **핵심 개념:** `for`로 페이지를 1~10까지 반복하면서 데이터를 하나씩 쌓는 것!

---

## 2. YouTube API — 키 필요 🎬

### 영상 검색하기 (`4.youtube.py`)

```python
import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

url = 'https://www.googleapis.com/youtube/v3/search'

params = {
    'part': 'snippet',       # 제목·설명 등 기본 정보 달라는 뜻
    'q': '파이썬 튜토리얼',   # 검색어
    'type': 'video',         # 영상만
    'maxResults': 50,        # 최대 50개
    'key': API_KEY
}

data = requests.get(url, params).json()

for item in data['items']:
    title    = item['snippet']['title']
    video_id = item['id']['videoId']
    url      = f"https://www.youtube.com/watch?v={video_id}"
    print(title, url)
```

### 조회수·좋아요 가져오기 (`5.youtube_detail.py`)

> YouTube API는 검색 API와 통계 API가 **따로** 분리되어 있음!

```python
video_api_url = 'https://www.googleapis.com/youtube/v3/videos'

params = {
    'part': 'statistics',  # 통계(조회수, 좋아요 등) 달라는 뜻
    'id': video_id,
    'key': API_KEY
}

video_data = requests.get(video_api_url, params=params).json()
view_count = video_data['items'][0]['statistics']['viewCount']  # 조회수
```

### 결과를 CSV 파일로 저장하기 (`6.yotube_save.py`)

```python
import csv

with open("search_result.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["title", "video_id", "video_url"])  # 첫 줄 = 헤더(컬럼명)
    writer.writerow([title, video_id, video_url])        # 실제 데이터
```

### CSV 읽어서 상세 통계 수집 (`7.youtube_detail_save.py`)

```python
import csv

# 이전에 저장한 CSV에서 video_id 읽어오기
video_ids = []
with open("search_result.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)  # 헤더를 key로 자동 인식해줌
    for row in reader:
        video_ids.append(row["video_id"])

# 여러 영상 ID를 한 번에 조회 (효율적!)
params = {
    'part': 'snippet,statistics',
    'id': ','.join(video_ids),  # ['id1','id2'] → 'id1,id2' 형태로 변환
    'key': API_KEY
}
```

---

## 3. Gemini AI API — AI한테 질문하기 🤖

### 구버전 vs 신버전

```python
# ❌ 구버전 (쓰지 마세요! deprecated 됨)
# pip install google-generativeai

# ✅ 신버전 (이걸 쓰세요!)
# pip install google-genai
```

### AI한테 질문하기 (`9.aistudio_new.py`)

```python
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="gemini-2.5-flash",   # 사용할 AI 모델
    contents="파이썬이 뭔지 초등학생도 이해하게 설명해줘"
)

print(response.text)  # AI 답변 출력
```

### YouTube 데이터를 AI로 분석하기 (`10.aistudio_youtube.py`)

```python
import csv
from google import genai

# 1단계: CSV에서 영상 데이터 읽기
videos = []
with open("video_stats.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        videos.append({
            "title":    row["title"],
            "views":    row["view_count"],
            "likes":    row["like_count"],
            "comments": row["comment_count"],
        })

# 2단계: 데이터를 AI 질문 안에 넣기
prompt = f"""
다음 유튜브 영상 데이터를 분석해줘:
1. 가장 인기 있는 영상은?
2. 어떤 주제가 반응이 좋은지?

영상 데이터: {videos}
"""

# 3단계: AI한테 보내기
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)
print(response.text)
```

> **핵심:** `f"...{변수}..."` (f-string) 안에 데이터를 넣으면
> 실제 데이터가 AI 질문 안에 포함되어 같이 전송됨!

---

## 4. 네이버 API 🟢

### 네이버 뉴스/블로그 검색하기 (`11.naver_search.py`)

> 네이버 API는 URL 파라미터 대신 **헤더**에 키를 넣는 방식!

```python
import requests
from dotenv import load_dotenv
import os

load_dotenv()

client_id     = os.getenv("NAVER_CLIENT_ID")
client_secret = os.getenv("NAVER_CLIENT_SECRET")

url = "https://openapi.naver.com/v1/search/news.json"   # 뉴스
# url = "https://openapi.naver.com/v1/search/blog.json" # 블로그

# 네이버는 키를 헤더에 담아서 보냄
headers = {
    "X-Naver-Client-Id":     client_id,
    "X-Naver-Client-Secret": client_secret
}

params = {"query": "생성형 AI"}

data = requests.get(url, headers=headers, params=params).json()
print(data)
```

---

## 5. 네이버 소셜 로그인 (OAuth 2.0) 🔐

### 소셜 로그인이 뭐야?

> "네이버로 로그인" 버튼을 눌렀을 때 일어나는 일

```
1. 내 앱 → "네이버로 로그인" 버튼 클릭
2. 네이버 로그인 페이지로 이동
3. 사용자가 네이버 아이디/비밀번호 입력
4. 네이버가 내 앱에 "code"를 전달
5. 내 앱이 code로 네이버에 "진짜 맞냐?" 확인
6. 네이버가 access_token 발급
7. access_token으로 사용자 정보 가져오기
```

### Flask로 구현 (`1.naverlogin/app.py`)

```python
from flask import Flask, redirect, request, session, url_for
import requests, os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("MY_SESSION_KEY")  # 세션 암호화 키

# 1. 로그인 버튼 → 네이버 로그인 페이지로 이동
@app.route('/login')
def naver_login():
    auth_url = (
        "https://nid.naver.com/oauth2.0/authorize?"
        f"response_type=code"
        f"&client_id={os.getenv('NAVER_CLIENT_ID')}"
        f"&redirect_uri={os.getenv('NAVER_REDIRECT_URI')}"
        f"&state=RANDOM값"
    )
    return redirect(auth_url)

# 2. 네이버가 code를 들고 여기로 돌아옴
@app.route('/api/naver/callback')
def naver_callback():
    code = request.args.get("code")  # 네이버가 준 임시 코드

    # code로 access_token 교환
    token_resp = requests.get(
        f"https://nid.naver.com/oauth2.0/token?"
        f"grant_type=authorization_code"
        f"&client_id={os.getenv('NAVER_CLIENT_ID')}"
        f"&client_secret={os.getenv('NAVER_CLIENT_SECRET')}"
        f"&code={code}&state=RANDOM값"
    ).json()

    access_token = token_resp["access_token"]

    # access_token으로 사용자 정보 요청
    profile = requests.get(
        "https://openapi.naver.com/v1/nid/me",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    session["user"] = profile["response"]  # 세션에 저장
    return redirect("/")

# 3. 로그아웃
@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")
```

> **핵심:** 로그인 → code 받기 → access_token 교환 → 사용자 정보 조회
> 이 3단계가 OAuth 2.0의 전부!

---

## 6. 네이버 메일 (SMTP/IMAP) 📧

### 메일 보내기 (`2.navermail/1.sendmail.py`)

> **SMTP** = 메일을 **보내는** 프로토콜 (우체국에 편지 맡기기)

```python
import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = 'smtp.naver.com'
SMTP_PORT   = 587
NAVER_ID    = os.getenv('NAVER_MAIL_ID')
NAVER_PW    = os.getenv('NAVER_MAIL_APP_SECRET')  # 앱 비밀번호 사용!
EMAIL       = f'{NAVER_ID}@naver.com'

# 이메일 내용 작성 (HTML 형식도 가능)
message            = MIMEText("<h1>안녕하세요!</h1>", 'html', _charset='utf-8')
message['Subject'] = "파이썬으로 보낸 메일"
message['From']    = EMAIL
message['To']      = EMAIL  # 받을 주소

try:
    smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    smtp.starttls()  # 보안 연결 시작 (필수!)
    smtp.login(NAVER_ID, NAVER_PW)
    smtp.sendmail(EMAIL, EMAIL, message.as_string())
    print("메일 전송 성공!")
except Exception as e:
    print(f"오류: {e}")
finally:
    smtp.quit()  # 연결 종료 (finally = 오류가 나도 반드시 실행)
```

### 메일 읽기 (`2.navermail/2.readmail.py`)

> **IMAP** = 메일을 **읽는** 프로토콜 (우편함에서 편지 꺼내기)

```python
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv
import os

load_dotenv()

NAVER_ID = os.getenv('NAVER_MAIL_ID')
NAVER_PW = os.getenv('NAVER_MAIL_APP_SECRET')
EMAIL    = f'{NAVER_ID}@naver.com'

# IMAP으로 메일함 접속
mail = imaplib.IMAP4_SSL('imap.naver.com', 993)
mail.login(EMAIL, NAVER_PW)
mail.select('INBOX')  # 받은 메일함 선택

# 전체 메일 목록 가져오기
status, messages = mail.search(None, "ALL")
mail_ids    = messages[0].split()
latest_id   = mail_ids[-1]  # 가장 마지막(최신) 메일

# 메일 내용 가져오기
status, msg_data = mail.fetch(latest_id, "(RFC822)")

for part in msg_data:
    if isinstance(part, tuple):
        msg = email.message_from_bytes(part[1])

        # 제목 디코딩 (한글 깨짐 방지)
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8")

        print("발신자:", msg.get("From"))
        print("제목:",   subject)

        # 본문 추출
        if not msg.is_multipart():
            body = msg.get_payload(decode=True).decode('utf-8')
            print("본문:", body)
```

---

## 전체 흐름 한눈에 보기 🗺️

```
[GitHub API]
특정 유저 레포 조회 → 키워드 검색 → 여러 페이지 수집

[YouTube API]
영상 검색(search) → 상세 통계(videos) → CSV 저장 → AI 분석

[Gemini AI API]
질문 전송 → AI 답변 받기 → 데이터 분석에 활용

[네이버 API]
검색(뉴스/블로그) → 소셜 로그인(OAuth) → 메일 보내기/읽기
```

---

## 핵심 문법 4가지만 기억하자 💡

### 1. API 요청하는 법

```python
# GET 요청 (데이터 가져오기)
response = requests.get(URL, params=파라미터딕셔너리)
data = response.json()  # 받은 JSON을 파이썬 딕셔너리/리스트로 변환
```

### 2. 딕셔너리에서 데이터 꺼내는 법

```python
# data = {'items': [{'snippet': {'title': '제목'}}]}
title = data['items'][0]['snippet']['title']
#             ↑키     ↑0번째   ↑키        ↑키
#        대괄호로 한 단계씩 파고들기!
```

### 3. CSV 저장 / 읽기

```python
# 저장
with open("파일명.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["컬럼1", "컬럼2"])  # 헤더
    writer.writerow([값1, 값2])          # 데이터

# 읽기 (헤더를 key로 자동 인식)
with open("파일명.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["컬럼1"])
```

### 4. f-string으로 데이터를 문자열에 넣기

```python
name = "홍길동"
age  = 25

# 중괄호 {} 안에 변수를 넣으면 값이 그대로 들어감
print(f"안녕하세요, {name}님! 나이는 {age}살이네요.")
# 출력: 안녕하세요, 홍길동님! 나이는 25살이네요.
```

---

## 자주 하는 실수 ⚠️

| 실수 | 올바른 방법 |
|------|-------------|
| API 키를 코드에 직접 씀 | `.env` 파일에 저장 후 `os.getenv()` 사용 |
| `.env`를 깃허브에 올림 | `.gitignore`에 `.env` 추가 |
| 구버전 `google-generativeai` 사용 | 신버전 `google-genai` 사용 |
| 네이버 메일에 일반 비밀번호 사용 | 네이버 앱 비밀번호 발급해서 사용 |
| `resp.json()` 없이 데이터 사용 | 반드시 `.json()` 으로 변환 후 사용 |
