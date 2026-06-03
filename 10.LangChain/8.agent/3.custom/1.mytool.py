from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent 

load_dotenv()

@tool
def calculator(expression: str) -> str:
    """수학 식을 계산한다. 예: 53 * 7 + 2 """
    try:
        # 예외처리를 잘 하지 않으면, LLM 이 지멋대로 입력하는 값으로 우리 코드가 죽을(crash) 수 있음
        # return str(eval(expression))
        return str(eval(expression, {"__builtins__": {}}, {})) # 내부 빌트인 함수들의 호출을 금지한다.
        # return str(eval("__import__('os').system('del hello.txt"))
    except Exception as e:
        return f"계산 오류: {e}"

llm = ChatOpenAI(model="gpt-4o-mini")
agent = create_agent(llm, [calculator])

result = agent.invoke({
    "messages": [("user", "10 나누기 2 곱하기 5는?")]
})

print("최종답변: ", result['messages'][-1].content)
