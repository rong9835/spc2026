import openai
from dotenv import load_dotenv
import os
import base64

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai_api_key)

# 이런 변환함수를 일일이 다 암기할 필요는 XX. 인코딩 알아야함. 왜 해야하는지도..
def encode_image_to_base64(image_path):
    # 이미지를 읽어서 base64로 인코딩 하는 함수 구현
    with open(image_path, "rb") as file:
        base64_bytes = base64.b64encode(file.read()).decode('utf-8')
        return f"data:image/jpeg;base64,{base64_bytes}"

def ask_chatbot(image_path, user_input):
    image_base64 = encode_image_to_base64(image_path)

    final_message = [
        {'role': 'system', 'content': '당신의 스포츠 트레이너이자 국가대표 스포츠 평가위원 입니다.'},
        {'role': 'user', 'content': [
            {
                "type": "text",
                "text": user_input
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": image_base64   # 사진을 base64로 인코딩한 텍스트...
                }
            }
        ]}
    ]
    # print(final_message)

    response = client.chat.completions.create(
        model='gpt-4.1-mini',  # gpt-4 시리즈부터 이미지를 지원함 (멀티모달)
        messages=final_message
    )

    final_response = response.choices[0].message.content
    return final_response

# image_path="cat.jpg"
# question="여기에는 몇마리의 동물이 있나요?"
# print(ask_chatbot(image_path, question))

image_path="squats-good.jpg"
question="나의 운동자세가 어떤지 전문가 입장으로 점수를 10점 만점에 몇점인지 평가해주고, 해석해주세요. 답변은 꼭 한국말로 해주세요."

print(ask_chatbot(image_path, question))

print('-' * 60)

image_path="squats-bad.jpg"
question="나의 운동자세가 어떤지 전문가 입장으로 점수를 10점 만점에 몇점인지 평가해주고, 해석해주세요. 답변은 꼭 한국말로 해주세요. 혹시 평가를 할 수 없는 경우에는 왜 그런지 이유도 상세하게 설명하시오."

print(ask_chatbot(image_path, question))
