from flask import Flask, render_template, redirect, request, session, url_for
from dotenv import load_dotenv
import requests
import os

load_dotenv()

client_id = os.getenv('NAVER_CLIENT_ID')
client_secret = os.getenv('NAVER_CLIENT_SECRET')
callback_uri = os.getenv('NAVER_REDIRECT_URI')

naver_auth_url = 'https://nid.naver.com/oauth2.0/authorize'
naver_token_url = 'https://nid.naver.com/oauth2.0/token'
naver_profile_url = 'https://openapi.naver.com/v1/nid/me'

app = Flask(__name__)
app.secret_key = os.getenv("MY_SESSION_KEY")

@app.route('/')
def index():
    user = session.get('user')
    return render_template('index.html', user=user)

@app.route('/api/naver/callback')
def naver_callback():
    code = request.args.get("code")
    state = request.args.get("state") # 내가 준 값이 맞는지 봐야 하는데, 오늘은 귀찮아서 통과

    # 이 code를 들고 네이버한테 "니가 준거 맞냐" 고 물어보러 간다
    token_url = (
        f"{naver_token_url}?"
        f"grant_type=authorization_code&client_id={client_id}"
        f"&client_secret={client_secret}&code={code}&state={state}"
    )

    token_response = requests.get(token_url).json()
    access_token = token_response.get("access_token")
    print(access_token)

    # 나와 저 사용자에 대한 검증이 끝나서, 나는 네이버와 대화할수 있는 인증토큰(access_token) 을 받아왔음. 이제 이걸로, 우리 고갱님의 정보를 물어본다...
    profile_url = (
        f"{naver_profile_url}"
    )

    headers = {"Authorization": f"Bearer {access_token}"}

    profile = requests.get(profile_url, headers=headers).json()
    print("서버측 사용자 정보 응답: ", profile)

    # 그럼, 필수동의 항목은 다 받아올수 있고, 선택 동의항목은, 사용자가 동의하고 가입했다면, 받아올수 있고, 동의 안했으면 네이버가 안줌..
    session["user"] = profile["response"]

    return redirect(url_for('index'))

@app.route('/login')
def naver_login():

    auth_url = (
        f"{naver_auth_url}?"
        f"response_type=code&client_id={client_id}"
        f"&redirect_uri={callback_uri}&state=HELLO"
    )

    print(auth_url)
    return redirect(auth_url)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
