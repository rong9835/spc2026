from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_tavily import TavilySearch

load_dotenv()

# 구글 검색은 원래 구글API 키로 하면 됨.
# => 이걸 쉽게 만들어주는 다양한 사이트가 있음.. Serf, Serper, Tavily

# pip install langchain-tavily
# TAVILY_API_KEY=tvly-dev-loHJz-xxxxx

web_search = TavilySearch(max_results=3)
llm = ChatOpenAI(model="gpt-4o-mini")
agent = create_agent(llm, [web_search])

result = agent.invoke({"messages": [("user", "LangChain 의 최신 버전은??")]})
print(result["messages"][-1].content)
