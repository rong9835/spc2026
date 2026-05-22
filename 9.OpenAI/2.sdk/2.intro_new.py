# pip uninstall openai; pip install openai    # 현재 최신은 4.x
import openai

from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=openai_api_key)

response = client.chat.completions.create(
    model='gpt-3.5-turbo',
    messages=[
        {'role': 'system', 'content': '당신의 나의 질문에 답변을 잘 하는 챗봇입니다.'},
        {'role': 'user', 'content': '안녕하세요, 반갑습니다.'}
    ]
)

final_response = response.choices[0].message.content
print(final_response)
