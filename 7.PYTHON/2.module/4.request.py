# 외부 모듈은 pip install requests 로 설치한다
# 그러면, pypi.org로 부터 다운로드 받아서, 나의 "가상환경" 에 설치가 됨.
import requests

# 외부에 HTTP 요청을 대신 해주는 라이브러리
# resp = requests.get("http://www.example.com")
# print("웹 페이지 내용: ", resp.text)

resp = requests.get('https://api.github.com')
if (resp.status_code == 200):
    print(resp.text)
else:
    print("해당 페이지를 가져오는데 실패했습니다. code: ", resp.status_code)
