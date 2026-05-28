from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI 
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

llm = ChatOpenAI(model='gpt-4o-mini')

prompt = [
    SystemMessage(content="당신은 경력 10년차 호텔 쉐프입니다."),
    HumanMessage(content="오늘 저녁 메뉴를 추천해줘."),
    AIMessage(content="비빔밥은 어떠신가요?"),
    HumanMessage(content="아~ 좋아. 그걸 만들기 위한 재료는?"),
]

result = llm.invoke(prompt)
print(result.content)
