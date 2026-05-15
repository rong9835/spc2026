# pip install python-dotenv

import os
import requests
from dotenv import load_dotenv

# .env 로드
load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

# API URL
search_url = 'https://www.googleapis.com/youtube/v3/search'
video_api_url = 'https://www.googleapis.com/youtube/v3/videos'

# 검색어
search_query = "파이썬 튜토리얼"

# Search API 요청 파라미터
search_params = {
    'part': 'snippet',
    'q': search_query,
    'type': 'video',
    'maxResults': 50,
    'key': API_KEY
}

# 검색 요청
response = requests.get(search_url, params=search_params)

# JSON 변환
data = response.json()

# 검색 결과 저장
search_results = data['items']

# 최종 결과 저장용
table = []

# 테이블 헤더
table_header = ['index', 'title', 'view count', 'video url']

# 각 영상 상세 조회
for index, result in enumerate(search_results, start=1):

    # 제목
    title = result['snippet']['title']

    # 비디오 ID
    video_id = result['id']['videoId']

    # 실제 유튜브 URL
    youtube_watch_url = f'https://www.youtube.com/watch?v={video_id}'

    # videos API 요청 파라미터
    video_params = {
        'part': 'statistics',
        'id': video_id,
        'key': API_KEY
    }

    # videos API 호출
    video_response = requests.get(
        video_api_url,
        params=video_params
    )

    print(video_response)

    # JSON 데이터 변환
    video_data = video_response.json()

    # 조회수 추출
    if 'items' in video_data and video_data['items']:
        view_count = video_data['items'][0]['statistics']['viewCount']
    else:
        view_count = 'N/A'

    # 테이블 저장
    table.append([index, title, view_count, youtube_watch_url])

# 출력
print(table_header)

for row in table:
    print(row)
