# API 핵심 정리 (왕초보용)

---

## API가 뭐야?

> 식당으로 비유하면:
> - **나** = 손님
> - **API 서버** = 주방
> - **API 요청** = 주문
> - **API 응답** = 음식이 나오는 것

내가 "이 데이터 줘!" 하고 요청하면, 서버가 데이터를 돌려주는 것.

---

## API 키가 뭐야?

> "나 허락받은 사람이에요" 라는 **출입증** 같은 것.

YouTube, Gemini 같은 유료/제한 API는 키가 있어야 사용 가능.  
GitHub API는 키 없이도 사용 가능 (단, 횟수 제한 있음).

---

## API 키는 어떻게 관리해?

> 코드에 직접 쓰면 절대 안 됨! (깃허브에 올리면 다 보임 = 위험)

**방법: `.env` 파일에 따로 보관**

```
# .env 파일 (이 파일은 절대 깃허브에 올리면 안 됨)
YOUTUBE_API_KEY=내키값
GEMINI_API_KEY=내키값
```

```python
# 코드에서 꺼내 쓰는 법
from dotenv import load_dotenv
import os

load_dotenv()                          # .env 파일 읽기
API_KEY = os.getenv("YOUTUBE_API_KEY") # 키 가져오기
```

---

## 1. GitHub API - 코드 없이 사용 가능!

**1.githubapi.py** - 특정 유저의 레포 목록 가져오기

```python
import requests

# 이 URL에 GET 요청을 보내면 데이터를 줌
url = "https://api.github.com/users/rong9835/repos"

resp = requests.get(url)   # 요청 보내기
repos = resp.json()        # 받은 데이터를 파이썬이 읽을 수 있게 변환

for repo in repos:
    print(repo["name"])    # 레포 이름 출력
    print(repo["html_url"]) # 레포 주소 출력
```

**2.github_search.py** - 키워드로 레포 검색하기

```python
import requests

url = 'https://api.github.com/search/repositories'

params = {
    'q': 'chatbot',   # 검색어
    'per_page': 100,  # 한 번에 100개
    'page': 1         # 1페이지
}

resp = requests.get(url, params)
data = resp.json()

# 검색결과는 data['items'] 안에 있음
for repo in data['items']:
    print(repo['name'])
```

**3.github_search2.py** - 여러 페이지 한꺼번에 가져오기

```python
# 1페이지, 2페이지, 3페이지... 10페이지까지 반복해서 다 모음
all_repos = []

for page in range(1, 11):   # 1 ~ 10페이지
    params = {'q': 'chatbot', 'per_page': 100, 'page': page}
    resp = requests.get(url, params)
    data = resp.json()

    if 'items' in data:               # 결과가 있을 때만
        all_repos += data['items']    # 리스트에 추가
```

---

## 2. YouTube API - 키 있어야 함

**4.youtube.py** - 유튜브 영상 검색하기

```python
import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

url = 'https://www.googleapis.com/youtube/v3/search'

params = {
    'part': 'snippet',       # 제목, 설명 등 기본 정보 달라는 뜻
    'q': '파이썬 튜토리얼',   # 검색어
    'type': 'video',         # 영상만
    'maxResults': 50,        # 최대 50개
    'key': API_KEY           # 내 키
}

response = requests.get(url, params)
data = response.json()

for item in data['items']:
    title = item['snippet']['title']              # 제목
    video_id = item['id']['videoId']              # 영상 고유 ID
    video_url = f"https://www.youtube.com/watch?v={video_id}"  # 실제 URL
    print(title, video_url)
```

**5.youtube_detail.py** - 각 영상의 조회수까지 가져오기

```python
# 검색 API로 영상 목록 → videos API로 조회수 따로 가져옴
video_api_url = 'https://www.googleapis.com/youtube/v3/videos'

params = {
    'part': 'statistics',  # 조회수, 좋아요 등 통계 달라는 뜻
    'id': video_id,
    'key': API_KEY
}

video_data = requests.get(video_api_url, params=params).json()
view_count = video_data['items'][0]['statistics']['viewCount']  # 조회수
```

**6.yotube_save.py** - 검색 결과를 CSV 파일로 저장하기

```python
import csv

# CSV 파일로 저장
with open("search_result.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["title", "video_id", "video_url"])  # 첫 줄 = 헤더
    writer.writerow([title, video_id, video_url])        # 데이터 저장
```

**7.youtube_detail_save.py** - 저장된 CSV 읽어서 통계 수집하기

```python
import csv

# 이전에 저장한 CSV에서 video_id 읽어오기
video_ids = []
with open("search_result.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)   # 헤더를 key로 자동 인식
    for row in reader:
        video_ids.append(row["video_id"])

# 여러 영상 한 번에 조회 (효율적!)
params = {
    'part': 'snippet,statistics',
    'id': ','.join(video_ids),   # ['id1','id2'] → 'id1,id2'
    'key': API_KEY
}
```

---

## 3. Gemini AI API - AI한테 질문하기

**8.aistudio_old.py** vs **9.aistudio_new.py**

> 구버전 쓰지 말고, 신버전으로 쓰자!

```python
# ❌ 구버전 (쓰지 마세요)
# pip install google-generativeai

# ✅ 신버전 (이걸 쓰세요)
# pip install google-genai

from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="파이썬이 뭔지 쉽게 설명해줘"
)

print(response.text)  # AI 답변 출력
```

---

## 4. AI + YouTube 데이터 합치기

**10.aistudio_youtube.py** - 수집한 데이터를 AI로 분석하기

```python
# 1. CSV에서 영상 데이터 읽기
videos = []
with open("video_stats.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        videos.append({
            "title": row["title"],
            "views": row["view_count"],
            "likes": row["like_count"],
        })

# 2. AI한테 분석 요청 (데이터를 프롬프트에 넣기)
prompt = f"""
다음 유튜브 영상 데이터를 분석해줘:
1. 가장 인기 있는 영상은?
2. 인기 있는 이유는?

데이터: {videos}
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)
print(response.text)
```

> **핵심:** f-string `f"..."` 안에 `{변수}` 넣으면 실제 데이터가 AI 질문 속에 들어감!

---

## 전체 흐름 한눈에 보기

```
1단계: YouTube로 영상 검색
        ↓
2단계: 검색 결과를 CSV 파일에 저장
        ↓
3단계: CSV 파일에서 video_id 읽어서 상세 통계 수집
        ↓
4단계: 통계 데이터를 CSV로 저장
        ↓
5단계: 저장한 데이터를 Gemini AI한테 넘겨서 분석 요청
```

---

## 핵심 문법 3가지만 기억하자

### 1. API 요청하는 법
```python
response = requests.get(URL, params=파라미터딕셔너리)
data = response.json()  # 받은 데이터를 파이썬 딕셔너리/리스트로 변환
```

### 2. 딕셔너리에서 데이터 꺼내는 법
```python
# data = {'items': [{'snippet': {'title': '제목'}}]}
title = data['items'][0]['snippet']['title']
#        ↑키      ↑인덱스  ↑키         ↑키
```

### 3. CSV 저장/읽기
```python
# 저장
with open("파일명.csv", "w", ...) as file:
    writer = csv.writer(file)
    writer.writerow([값1, 값2])

# 읽기
with open("파일명.csv", "r", ...) as file:
    reader = csv.DictReader(file)
    for row in reader:
        print(row["컬럼명"])
```
