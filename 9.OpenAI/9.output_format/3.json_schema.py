import os
import json

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 내가 원하는 출력 형식 - 즉 자료구조를 정의 (json_schema 를 정의 하였음)
city_schema = {
    'type': 'object',
    'properties': {   # 내가 원하는 변수 및 데이터 타입
        'name':         {'type': 'string'},
        'population':   {'type': 'integer'},
        'area_km2':     {'type': 'number'},
    },
    'required': ['name', 'population', 'area_km2'],  # 이 필드는 꼭 채울것
    'additionalProperties': False,           # 정의 하지 않은건 추가하지 말것
}

response = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[
        {'role':'system', 'content':'질문에 대해 JSON으로만 답변하시오.'},
        {'role':'user', 'content':'서울의 인구와 면적을 알려주시오.'},
    ],
    response_format={
        'type': 'json_schema',  # 출력 결과가 아래 정의한 나만의 스키마로 주도록 요청
        'json_schema': {
            'name': 'city_info',   # 내가 정의하는 이름
            'strict': True,        # 엄격하게 따라라
            'schema': city_schema
        }
    } 
)

answer = response.choices[0].message.content
# print(answer)

data = json.loads(answer)
print(f"도시의 이름: {data['name']} - 인구: {data['population']:,}명, 면적 {data['area_km2']}km2")
