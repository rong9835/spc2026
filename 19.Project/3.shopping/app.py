import os
from dotenv import load_dotenv

from flask import Flask, send_from_directory, jsonify, request

from openai import OpenAI
import requests

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
app = Flask(__name__, static_folder='public')


reviews = []  # 사용자들의 댓글을 저장할 변수 (평점과 후기가 함께 들어간다. {'rating': 값, 'comment': 값})


# ------------------
# API 라우팅
# ------------------
@app.route('/api/reviews', methods=['POST'])  # POST로 받기
def add_review():
    # reviews 에 저장하기
    data = request.get_json()
    rating = data['rating']
    comment = data['comment']
    reviews.append({'rating': rating, 'comment': comment})

    return jsonify({'message': '저장완료'})


@app.route('/api/reviews', methods=['GET'])  # GET으로 받기
def get_review():
    # reviews 를 가져와서 반환하기

    return jsonify({'data': reviews})


@app.route('/api/ai-summary')  # GET으로 받기
def get_ai_summary():
    # reviews를 가져와서....
    # 여기에서 프롬프트 및 api 호출 코드 작성
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {
                'role': 'system',
                'content': '너는 쇼핑몰 리뷰를 요약해주는 AI야',
            },
            {'role': 'user', 'content': str(reviews)},
        ],  # 변수 이름
    )
    return jsonify({'message': response.choices[0].message.content})


# ------------------
# 웹 서비스 라우팅
# ------------------
@app.route('/')
def index():
    return send_from_directory('public', 'index.html')


if __name__ == '__main__':
    app.run(debug=True)
