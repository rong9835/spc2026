# pip install wikipedia

import wikipedia

from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import create_agent   # 이 함수가 3번이상 바뀌었음.. create_react_agent, initailize_agent

tools = load_tools(["wikipedia"])

llm = ChatOpenAI(model="gpt-4o-mini")
agent = create_agent(llm, tools)

result = agent.invoke({"message": [("user", "파이썬 프로그래밍 언어는 누가 만들었어?")]})
print(result)
