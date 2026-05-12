import requests
from bs4 import BeautifulSoup
import csv

url = "https://www.naver.com"

resp = requests.get(url)
resp.encoding = "utf-8"  # 유니코드 글자로 인식시켜서 깨지는 글자 제거

soup = BeautifulSoup(resp.text, "html.parser")
print(soup)

news = soup.select(".MediaNewsView-module__desc_list___uQ3r1")
print(news)
