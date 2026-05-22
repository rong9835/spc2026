from dotenv import load_dotenv
import requests
import os

load_dotenv()

client_id = os.getenv("NAVER_CLIENT_ID")
client_secret = os.getenv("NAVER_CLIENT_SECRET")

text = "생성형 AI"
# url = "https://openapi.naver.com/v1/search/blog.json"
url = "https://openapi.naver.com/v1/search/news.json"

headers = {
    "X-Naver-Client-Id": client_id,
    "X-Naver-Client-Secret": client_secret
}

params = {
    "query": text
}

response = requests.get(url, headers=headers, params=params)
# print(response)
data =response.json()

print(data)
