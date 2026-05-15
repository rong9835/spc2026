# pip install google-genai
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="나는 한국에 살고 있는, 20대 개발자야. 오늘 저녁에 뭐 먹으면 좋은지 알려줘"
)

print(response.text)
