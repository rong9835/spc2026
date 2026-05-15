# pip install python-dotenv

import csv
import os
import requests
from dotenv import load_dotenv

load_dotenv() # .env파일을 읽어서 해당 key/value 를 메모리(환경변수)에 올려둠

API_KEY = os.getenv("YOUTUBE_API_KEY")

url = 'https://www.googleapis.com/youtube/v3/search'

search_query = "파이썬 튜토리얼"

params = {
    'part': 'snippet',
    'q': search_query,
    'type': 'video',
    'maxResults': 50,
    'key': API_KEY
}

response = requests.get(url, params)
data = response.json()
print(data)

# csv에 저장
with open("search_result.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["title", "video_id", "video_url", "description"])

    for item in data['items']:
        title = item['snippet']['title']
        video_id = item['id']['videoId']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        description = item['snippet']['description']

        print(f'제목: {title}, URL: {video_url}, 설명: {description}')
        print('-'*40)

        writer.writerow([title, video_id, video_url, description])

