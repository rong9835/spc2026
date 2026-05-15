# pip install google-generativeai  <-- 이건 사실 deprecated 임
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

response = model.generate_content("파이썬이 무엇인지 초등학생도 이해하기 쉽게 설명해줘")

print(response.text)
