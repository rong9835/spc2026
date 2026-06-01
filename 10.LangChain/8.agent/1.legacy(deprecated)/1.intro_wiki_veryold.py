# 에이전트를 통해서, 본연의 LLM 즉 대화의 기능 외적인 기능을 쓸수 있음

# pip install wikipedia

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import initialize_agent, AgentType

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")

tools = load_tools(["wikipedia"])

# 에이전트 초기화
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True   # 나중에는 False 할건데, 지금은 이 에이전트의 생각을 보기 위해서...
)

result = agent.invoke({"input": "인공지능의 역사에 대해 간략히 설명해줘."})
print(result["output"])
