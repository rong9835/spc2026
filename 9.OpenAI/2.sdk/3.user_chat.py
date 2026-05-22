# pip uninstall openai; pip install openai    # 현재 최신은 4.x
import openai

from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=openai_api_key)

def ask_chatbot(user_input):
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'system', 'content': '당신의 나의 질문에 답변을 잘 하는 챗봇입니다.'},
            {'role': 'user', 'content': user_input}
        ]
    )

    final_response = response.choices[0].message.content
    return final_response

while True:
    user_input = input("\n질문: ").strip()
    chatbot_response = ask_chatbot(user_input)
    print("챗봇응답: ", chatbot_response)
