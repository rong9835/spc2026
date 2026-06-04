# whisper (속삭임) 말~~을 기반으로 text 로 변환 : STT (Speech-to-text)

import os
import base64

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

def transcribe_audio(file): # 오디오를 설명하시오
    with open(file, "rb") as af:   # af = audio file
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=af,
            response_format="text",  # json, 등등...
            language="ko"   # 한국어
        )
    return transcript

result = transcribe_audio("harvard.wav")
result = transcribe_audio("Track021_생각해봐요.mp3")
print("결과: ", result)
