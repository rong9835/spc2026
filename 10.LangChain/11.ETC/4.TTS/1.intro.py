import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

text = """
안녕하세요. 지금은 OpenAI의 TTS 음성 합성 품질을 테스트하는 중입니다.

오늘은 오전 9시 35분에 회의를 시작했고, 참석자는 총 27명이었습니다.

이번 프로젝트의 이름은 "AI-X 프로젝트랩 2026"이며, 백엔드는 Flask, 프론트엔드는 JavaScript로 개발하고 있습니다.

현재 서버의 CPU 사용률은 37.5퍼센트이고, 메모리는 12.8기가바이트를 사용 중입니다.

사용자는 "챗GPT"라고 입력했지만, 실제 서비스 이름은 "ChatGPT"입니다.

이번 주 금요일 오후 2시에 GitHub 저장소를 업데이트한 뒤 Pull Request를 생성할 예정입니다.

저의 이메일 주소는 sample-test@example.com 이고, 웹사이트 주소는 https://example.com 입니다.

오늘 점심 메뉴는 김치찌개, 된장찌개, 그리고 치킨 샐러드였습니다.

AWS의 EC2 인스턴스와 RDS 데이터베이스를 연동한 후, API 응답 속도를 측정해 보겠습니다.
"""

response = client.audio.speech.create(
    model='tts-1',
    voice='alloy',    # 다양한 목소리
    input=text
)

response.write_to_file('output.mp3')
print('저장완료')
