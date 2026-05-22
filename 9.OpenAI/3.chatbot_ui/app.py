from flask import Flask, request, jsonify, send_from_directory
import openai
import os
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__, static_folder='static', static_url_path='') # static 폴더 경로와 그 prefix 를 결정(변경) 할 수 있음

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    chat_message = data.get('chatMessage', '')
    print("사용자 입력값: ", chat_message)

    # chatgpt 에게 물어보기...
    gpt_reply = ask_chatgpt(chat_message)

    return jsonify({'reply': f'{gpt_reply}'})

def ask_chatgpt(chat_message):
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # 왠만한 우리 실습은 gpt-4o-mini
        messages = [
            {"role": "system", "content": "당신은 친절한 챗봇입니다. 경상도 사투리를 적절하게 섞어서 답변하시오."},
            {"role": "user", "content": chat_message}
        ]
    )
    print("출력확인:", response)
    return response.choices[0].message.content


if __name__ == '__main__':
    app.run(debug=True)
