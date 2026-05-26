# openai 기본 틀 불러온다 (dotenv)
# flask 기본 틀 짠다

import os
import json
from dotenv import load_dotenv

from openai import OpenAI

from flask import Flask, send_from_directory
from flask import request, Response

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
app = Flask(__name__, static_folder='public')

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/stream', methods=['POST'])
def stream():
    user_message = request.json.get('message', '')
    print(user_message)
    # openAI 에게 물어보고...

    def generate_response():
        # 아래 부분도 try except 로 감싸주어야함. 지금은 생략
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {'role': 'system', 'content': '당신은 친절한 AI도우미입니다.'},
                {'role': 'user', 'content': user_message }
            ],
            stream=True
        )
        for chunk in response:
            content = chunk.choices[0].delta.content
            print(content)
            if content:
                yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return Response(generate_response(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(debug=True)
