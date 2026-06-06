# 외부에 ollama 서버가 있는 경우... 나의 req를 api 에 요청하듯이 하면 됨..

import requests

OLLAMA_HOST = "http://192.168.0.153:11434"
OLLAMA_ENDPOINT = f"{OLLAMA_HOST}/api/generate"

payload = {
    "model": "exaone3.5",   # 필요한 모델 선택
    "prompt": "파이썬으로 구현하는 헬로우 월드 코드를 보여줘.",
    "stream": False
}

response = requests.post(OLLAMA_ENDPOINT, json=payload)
data = response.json()

print("모델 응답: ", data.get('response'))
