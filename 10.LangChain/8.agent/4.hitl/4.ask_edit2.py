from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent 
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage

load_dotenv()

checkpoint = MemorySaver()

@tool
def send_payment(recipient: str, amount: int) -> str:
    """ 수신자에게 지정 금액을 송금한다."""
    return f"{recipient} 에게 {amount} 원 송금 완료"

@tool
def get_balance(account: str) -> int:
    """ 계좌 잔액 조회 """
    return {"alice": 1_000_000, "bob": 500_000}.get(account, 0)

llm = ChatOpenAI(model="gpt-4o-mini")
agent = create_agent(llm, [send_payment, get_balance], checkpointer=checkpoint, interrupt_before=["tools"])

config = {"configurable": {"thread_id": "t001"}}

question = "bob에게 1만원을 송금해."

print(f"[유저] {question}")
result = agent.invoke({"messages": [("user", question)]}, config=config)
print('=' * 30)
print(result)
print('=' * 30)

# 1. 현재 멈춰 있는 상태 조회
ai_msg = agent.get_state(config).values["messages"][-1]
call = ai_msg.tool_calls[0]
args = call['args']

print(f"[에이전트 제안] {call['name']} ({call['args']})")


# 2. 해당 상태를 어떻게 처리할건지, 사용자에게 물어보기
print(f"\n{args['recipient']} 에게 송금을 진행하시겠습니까?")
print("  1. 예(송금)")
print("  2. 아니오(취소)")
print("  3. 금액 수정")
choice = input("선택 (1/2/3): ").strip()

if choice == "2":
    print("\n[취소] 사용자 요청에 의해 취소되었습니다.")
else:
    if choice == "3":
        new_amount = int(input("새 송금 금액(원) 을 입력하세요: ").strip())
        edited = {**call, "args": {**call['args'], 'amount': new_amount}}

        fixed = AIMessage(content=ai_msg.content, tool_calls=[edited], id=ai_msg.id)
        agent.update_state(config, {"messages": [fixed]})
        print(f"사람이 수정했음 10000 -> {new_amount}")

    # 3. 다시 이어서 실행한다.
    result = agent.invoke(None, config=config)  # 할일을 계속 이어서 하시오
    final = result["messages"][-1].content
    if not final:
        final = result["messages"][-2].content
    print(f"[최종] {final}")
