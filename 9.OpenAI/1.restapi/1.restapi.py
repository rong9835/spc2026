from dotenv import load_dotenv
import os
import requests

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
user_input = "우리집에 새로운 강아지를 분양했어.. 강아지 이름을 뭐라고 지을까?? 후보군 5개를 알려줘."

response = requests.post(
    'https://api.openai.com/v1/chat/completions',
    json={
        'model': 'gpt-3.5-turbo',
        'messages': [
            {'role': 'system', 'content': '너는 나를 잘 도와주는 경력 20년차의 작명가야.'},
            {'role': 'user', 'content': user_input}
        ],
        'temperature': 1.0,
        'top_p': 0.5
    },
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai_api_key}'    # Basic 인증 = Basic Authorization
    }
)

data = response.json()
final_response = data['choices'][0]['message']['content']
print(final_response)
