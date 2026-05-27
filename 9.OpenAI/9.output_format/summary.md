# OpenAI 출력 형식 제어 핵심 요약

> AI의 답변을 내가 원하는 **형태**로 받아오는 방법들

---

## 왜 출력 형식이 중요한가?

AI가 답변을 돌려줄 때 기본적으로는 **자연어(일반 문장)** 로 옵니다.  
하지만 프로그램에서 사용하려면 **정해진 구조** 가 필요합니다.

```
일반 답변: "서울의 인구는 약 950만 명이고, 면적은 605km²입니다."
JSON 답변: {"name": "서울", "population": 9500000, "area_km2": 605}
```

JSON 형태로 받으면 `data['population']` 처럼 **바로 꺼내 쓸 수 있어요!**

---

## 방법 1 — 프롬프트로 부탁하기 (1.json_output.py)

```python
messages=[
    {'role': 'system', 'content': '질문에 대해 JSON으로만 답변하시오.'},
    {'role': 'user',   'content': '서울의 인구와 면적을 알려주시오.'},
]
```

### 비유
> 레스토랑에서 "접시에 담아주세요" 라고 **말**로 부탁하는 것.  
> 보통은 지켜주지만, 가끔 그냥 손으로 줄 수도 있어요 😅

**단점:** AI가 JSON 형식을 **무시**할 수도 있다. 100% 보장 안 됨.

---

## 방법 2 — API 옵션으로 강제하기 (2.json_output2.py)

```python
response_format={'type': 'json_object'}  # ← 이걸 추가!
```

### 비유
> 레스토랑 주문서에 **"반드시 접시에 담기"** 체크박스를 표시하는 것.  
> 시스템 자체가 강제하므로 무조건 지켜집니다!

**장점:** JSON 형식을 **API 레벨에서 보장**한다.  
**주의:** 시스템 프롬프트에 JSON 언급이 있어야 동작함.

---

## 방법 3 — 내 맘대로 구조 설계하기 (3.json_schema.py)

```python
city_schema = {
    'type': 'object',
    'properties': {
        'name':       {'type': 'string'},   # 문자열
        'population': {'type': 'integer'},  # 정수
        'area_km2':   {'type': 'number'},   # 소수 포함 숫자
    },
    'required': ['name', 'population', 'area_km2'],  # 이 필드는 필수!
    'additionalProperties': False,                    # 다른 필드 금지!
}

response_format={
    'type': 'json_schema',
    'json_schema': {
        'name': 'city_info',
        'strict': True,
        'schema': city_schema
    }
}
```

### 비유
> 레스토랑에 **도면을 그려서 주며** "이 그릇에, 이 칸에, 이 재료만 담아주세요" 라고 하는 것.

**장점:** 정확히 **내가 원하는 구조**로만 반환된다.  
**활용:** `json.loads(answer)` 로 파싱 후 딕셔너리처럼 사용.

```python
data = json.loads(answer)
print(data['name'])        # 서울
print(data['population'])  # 9500000
```

---

## 방법 4 — 파이썬 객체로 바로 받기 (4.pydantic_output.py)

```python
from pydantic import BaseModel

class CityInfo(BaseModel):  # 내가 원하는 구조를 클래스로 정의
    name: str
    population: int
    area_km2: float

# create 대신 parse 사용!
response = client.chat.completions.parse(
    model='gpt-4o-mini',
    messages=[...],
    response_format=CityInfo   # 클래스를 직접 전달
)

# content 대신 parsed 에서 꺼냄!
answer = response.choices[0].message.parsed
print(answer.name)        # data['name'] 아닌 answer.name 으로 접근
print(answer.population)
```

### 방법 3 vs 방법 4 비교

| 구분 | 방법 3 (json_schema) | 방법 4 (pydantic) |
|------|----------------------|-------------------|
| 정의 방식 | 딕셔너리로 직접 작성 | 파이썬 클래스 |
| 결과 받기 | `message.content` → `json.loads()` | `message.parsed` |
| 데이터 접근 | `data['name']` | `data.name` |
| 코드 길이 | 길다 | 짧고 깔끔하다 |

> 파이썬 클래스를 쓰면 더 깔끔하고 타입 오류도 자동으로 잡아줘요!

---

## 방법 5 — 함수 직접 호출시키기 (5.tool_calling.py)

AI가 답을 생성하는 대신, **"이 함수를 써라"** 고 지시하는 방법입니다.

```python
def get_weather(city):
    weather = {'서울': '맑음, 22도', '부산': '흐림, 25도'}
    return weather.get(city, '정보 없음')

tools = [
    {
        'type': 'function',
        'function': {
            'name': 'get_weather',
            'description': '특정 도시의 현재 날씨를 조회한다',
            'parameters': {
                'type': 'object',
                'properties': {
                    'city': {'type': 'string', 'description': '도시 이름'}
                },
                'required': ['city']
            }
        }
    }
]

response = client.chat.completions.create(
    ...,
    tools=tools,  # 사용할 수 있는 도구 목록을 전달
)

# AI가 함수를 호출할지 말지 결정함
if message.tool_calls:
    call = message.tool_calls[0]
    print(call.function.name)       # get_weather
    print(call.function.arguments)  # {"city": "서울"}
```

### 비유
> AI에게 "날씨가 궁금하면 기상청에 전화해" 라고 알려주는 것.  
> AI 스스로 판단해서 **필요할 때 함수를 호출**합니다.

**중요:** AI가 함수를 **직접 실행하는 게 아니라**, 함수를 실행하라는 **신호만** 줍니다.  
실제 실행은 우리 코드가 해야 합니다!

---

## 전체 비교 정리

| 방법 | 파일 | 특징 | 추천 상황 |
|------|------|------|-----------|
| 프롬프트 부탁 | 1번 | 간단, 보장 안 됨 | 테스트/학습 |
| json_object | 2번 | JSON 보장 | 구조 자유롭게 쓸 때 |
| json_schema | 3번 | 구조 완벽 제어 | 필드명·타입 엄격히 지정 |
| pydantic | 4번 | 파이썬 객체로 바로 사용 | **실무에서 가장 많이 씀** |
| tool_calling | 5번 | 외부 함수 연동 | AI + 실제 데이터 결합 |

---

## 핵심 키워드

| 키워드 | 설명 |
|--------|------|
| `response_format` | 출력 형식을 지정하는 API 옵션 |
| `json_object` | JSON 출력을 API 레벨에서 보장 |
| `json_schema` | 내가 직접 정의한 구조로 출력 강제 |
| `BaseModel` | Pydantic 라이브러리의 클래스, 데이터 구조 정의용 |
| `.parse()` | Pydantic 객체로 받을 때 사용 (create 대신) |
| `.parsed` | parse()로 받은 결과에서 객체 꺼낼 때 (.content 대신) |
| `tools` | AI가 사용할 수 있는 함수 목록 |
| `tool_calls` | AI가 함수 호출을 요청했는지 확인 |
