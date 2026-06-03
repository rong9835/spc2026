from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent 

load_dotenv()

@tool
def get_word_length(word: str) -> int:
    """ 단어을 글자 수를 세어서 숫자로 반환한다 """
    return len(word)

@tool
def calculate_tip(amount: float, percent: float) -> float:
    """ 음식점 영수증 금액과 팁 비율(%)을 입력받아서 팁 금액을 계산한다 
        안자값: 
            amount: 음식 가격 (원)
            percent: 팁 비율 (%)
        예시:
            10000원에 10% 팁은 = 1000원
    """
    return amount * percent / 100

@tool
def search_user(user_id: str) -> dict:
    """ 사용자 ID 로 사용자 정보를 조회한다. 존재하지 않으면 {} 빈 dict 를 반환한다."""
    db = {
        "u001": {"name": "홍길동", "city": "서울", "age": 30},
        "u002": {"name": "김철수", "city": "부산", "age": 20},
    }
    return db.get(user_id, {})

tools = [get_word_length, calculate_tip, search_user]
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools)

print("=== 툴 상태 확인 ===")
for t in tools:
    print(f"[Tool] {t.name}")
    print(f" 설명 : {t.description}")
    print(f" 인자 스키마: {t.args_schema.model_json_schema()}")

print("\n\n=== 툴 호출 ===")

questions = [
    "this-is-a-long-sentence 문장에 글자는 몇개야?",
    "5만원 영수증에 15% 팁을 주려면?",
    "홍길동 사용자 정보는?",
    "u001 사용자 정보는?"
]

name2tool = {t.name: t for t in tools}

for q in questions:
    r = llm_with_tools.invoke(q)
    print(f"[질문] {q}")
    for call in r.tool_calls:
        print(f" -> {call['name']} ({call['args']})")

        result = name2tool[call['name']].invoke(call['args'])  # 실제 실행!!
        print(f" -> 결과: {result}")
