# 텍스트를 기반으로 이미지를 생성... (GAN)

# 구버전 모델이 dall-e => dall-e-2 => ??
# gpt-image-1.5 또는 gpt-image-2
# 

import os
import base64

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

# prompt = """
# 노을 지는 해변, 잔잔한 파도, 수채화 스타일,
# 돌고래 3마리가 파도를 헤어치다가 그중 한마리가 점프해서 날개를 달고 날아가면서 하늘을 날고있는 갈매기때중
# 한마리를 잡아먹고 있음.
# 파도는 3층으로 가장 높음, 중간, 낮음 형태로 맨 앞에 파도가 가장 크고 뒤로 가면서 점점 줄어드는
# """

# 이런거 잘 안됨.
prompt = """
아이콘팩을 4x4로 해서 16개를 만들고... 64x64 크기로 해서, 해변, 조개, 등의 사물을 통해서 웹서비스 개발을 위한 아이콘 팩을 만들어줘.
"""

result = client.images.generate(
    model="gpt-image-1.5",
    prompt=prompt,
    size='1024x1024',  # 1024x1024 (정사각형), 1024x1536(세로), 1536/1024 가로
    quality='high'   # low / medium / high / auto
)

# image-2
# 4k 까지 지원함 (4096). 16:9 비율도 생성 가능...
# 지원 언어가 대폭 증가..
# 빠진 단점 하나는, 투명배경 못만듦.. 투명배경은 1.5의 기능임


b64 = result.data[0].b64_json
with open('output.png', 'wb') as f:
    f.write(base64.b64decode(b64))

print('저장 완료')
