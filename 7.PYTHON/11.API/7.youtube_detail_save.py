# pip install python-dotenv

import csv
import os
import requests
from dotenv import load_dotenv

# .env 로드
load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

# API URL
video_api_url = 'https://www.googleapis.com/youtube/v3/videos'

video_ids = []

with open("search_result.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        video_ids.append(row["video_id"])

# print(video_ids)

params = {
    "part": "snippet,statistics",
    "id": ",".join(video_ids),
    "key": API_KEY
}

response = requests.get(video_api_url, params)
data = response.json()

# 최종 결과 저장용
table = []

# 테이블 헤더
table_header = ['index', 'title', 'view_count', 'like_count', 'comment_count']

with open("video_stats.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(table_header)

    for item in data['items']:
        video_id = item['id']
        title = item["snippet"]["title"]
        stats = item["statistics"]
        view_count = stats.get("viewCount", 0)
        like_count = stats.get("likeCount", 0)
        comment_count = stats.get("commentCount", 0)

        writer.writerow([video_id, title, view_count, like_count, comment_count])