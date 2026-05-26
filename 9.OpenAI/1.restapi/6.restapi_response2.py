import os
import requests
from dotenv import load_dotenv


load_dotenv()


openai_api_key = os.getenv('OPENAI_API_KEY')


user_input = '대한민국의 수도는 어디야?'


response = requests.post(
    'https://api.openai.com/v1/responses',
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai_api_key}',
    },
    json={'model': 'gpt-4o-mini', 'input': user_input},
)


data = response.json()
print(data)
print('-' * 30)
answer = data['output'][0]['content'][0]['text']
print('응답:', answer)

response_id = data['id']
print('응답ID:', response_id)


user_input = '그 도시의 인구는 몇이야?'


response = requests.post(
    'https://api.openai.com/v1/responses',
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai_api_key}',
    },
    json={
        'model': 'gpt-4o-mini',
        'input': user_input,
        'previous_response_id': response_id,
    },
)

data = response.json()
print(data)
print('-' * 30)
answer = data['output'][0]['content'][0]['text']
print('응답:', answer)

response_id = data['id']
print('응답ID:', response_id)


user_input = '그 도시에서 가볼만한 곳 세곳만 추천해줄랜?'


response = requests.post(
    'https://api.openai.com/v1/responses',
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai_api_key}',
    },
    json={
        'model': 'gpt-4o-mini',
        'input': user_input,
        'previous_response_id': response_id,
    },
)

data = response.json()
print(data)
print('-' * 30)
answer = data['output'][0]['content'][0]['text']
print('응답:', answer)


print('응답ID:', data['id'])
