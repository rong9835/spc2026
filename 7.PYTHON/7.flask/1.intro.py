# pip install flask
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    5/0
    return """
    <html>
        <head>
            <title>타이틀</title>
            <style>
                p {
                    color: red;
                }
            </style>
        </head>
        <body>
            <H1>웰컴투 마이 홈</h1>
            <p>여기는 텍스트 본문이 들어갑니다.</p>
            <p>여기는 텍스트 본문22가 들어갑니다.</p>
        <body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True) # 이거 나중에 개발 끝나고 배포/운영하는곳에서는 꼭 제거되어야함.
