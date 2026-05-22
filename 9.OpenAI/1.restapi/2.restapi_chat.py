from dotenv import load_dotenv
import os
import requests

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')

def ask_chatbot(user_input):
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
    return final_response

# print(ask_chatbot("안녕하세요"))
# print(ask_chatbot("오늘은 2026년 5월 5일 어린이날입니다."))
# print(ask_chatbot("오늘은 무슨날인가요??"))

while True:
    user_input = input("\n당신의질문: ").strip()
    if user_input.lower() in ['quit', 'exit', '종료', '끝']:
        print("대화를 종료합니다. 안녕히 가세요.")
        break
    else:
        print("대화를 생성중입니다. 잠시만 기다려 주세요....")
        print("챗봇응답: ", ask_chatbot(user_input))
        print('-' * 60)
