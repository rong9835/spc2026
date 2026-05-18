# pip install flask-session
from flask import Flask, session
from flask_session import Session # 서버측에 세선을 저장하기 위한 확장 클래스

app = Flask(__name__)
app.secret_key = 'abcd1234' # 나만 아는 나의 세션 암호화 키. 이것도 .env에서 다루는것임.
app.config['SESSION_TYPE'] = 'filesystem'  # 나의 세션을 파일 / redis / memcahed / mongod 등등 다양한 걸 지원함
app.config['SESSION_FILE_DIR'] = './.sessions'  # 내가 정한 폴더명
app.config['SESSION_PERMANENT'] = False  # 브라우저 닫히면 삭제
app.config['SESSION_USE_SIGNER'] = True  # 세션 쿠키에 서명 사용

Session(app)

@app.route('/')
def main():
    if 'username' in session:
        return f"세션에서 당신의 정보를 찾았습니다. {session['username'], session['fullname'], session['hobby']}"

    session['username'] = 'spc2026'
    session['fullname'] = '홍길동'
    session['dob'] = '2020/05/05'
    session['hobby'] = '유투브하기,쇼핑하기,게임하기'

    return "첫 방문이시군요. 당신을 기억하겠습니다."

if __name__ == "__main__":
    app.run(debug=True)
