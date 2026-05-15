import os
import csv
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

videos = []

with open("video_stats.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        videos.append({
            "title": row["title"],
            "views": row["view_count"],
            "likes": row["like_count"],
            "comments": row["comment_count"],
        })

# 프롬프트 작성
prompt = f"""
다음 유부트 영상 데이터를 분석해서: 

1. 어떤 영상이 가장 인기가 있는지 
2. 인기있는 이유는 무엇인지
3. 어떤 주제가 반응이 좋은지 
4. 내가 유투브 채널을 운영하려고 하면, 어쩐 전략이 좋은지

를 자세히 분석해줘.

답변은 HTML로 포멧팅을 해줘.

영상 데이터: 
{videos}
"""

# print(prompt)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

print(response.text)
