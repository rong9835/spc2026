from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent

load_dotenv()

# 우리의 도구를 정의할때 @tool 데코레이터를 정의하고, 함수내에 주석을 쓰면, 그 내용을 읽어가서 본인이 해야할 일을 파악한다.
@tool
def calculator(expression):
    """ 수학 식을 계산한다. 예: 53 * 7 + 2 """
    return str(eval(expression))

llm = ChatOpenAI(model="gpt-4o-mini")
agent = create_agent(llm, [calculator])   # 나의 에이전트 

result = agent.invoke({
    # "messages": [("user", "다음의 수식에서 (50 * 5 + 5) 에서 5 를 나누면 얼마야?")]
    "messages": [("user", "복잡한 수식을 계산해줘. 50 에서 5를 곱하고 3을 나눈 다음에 다시 2를 빼고 그리고 5 를 나누면 얼마야?")]
})

print('=== 전체 메시지 흐름 ===')
for m in result["messages"]:
    if hasattr(m, "tool_calls") and m.tool_calls:
        for c in m.tool_calls:
            print(f"[도구 호출] {c['name']}({c['args']})")
    if m.content:
        prefix = {"human": "[사용자]", "ai": "[AI]", "tool": "[도구 결과]"}.get(m.type, m.type)

print(f"\n\n최종답변: {result['messages'][-1].content}")
