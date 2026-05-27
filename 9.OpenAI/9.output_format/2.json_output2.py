import os
import json

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

response = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[
        {'role':'system', 'content':'질문에 대해 JSON으로만 답변하시오.'},
        {'role':'user', 'content':'서울의 인구와 면적을 알려주시오.'},
    ],
    response_format={'type': 'json_object'} # 출력 결과가 OOO 탑이 되도록 API단에서 보장한다.
)

answer = response.choices[0].message.content
print(answer)
