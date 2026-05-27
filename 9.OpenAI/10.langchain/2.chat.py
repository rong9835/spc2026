import os
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import OpenAI      # 단발성 질문 (Instruct Model = gpt-3.5-turbo-instruct)
from langchain_openai import ChatOpenAI  # Q&A 용으로 사용 (Chat Model = gpt-3.5-turbo)

llm = OpenAI(model='gpt-3.5-turbo-instruct')
prompt = '다음 문장을 한국말로 번역해줘: Good Morning'
print(llm.invoke(prompt))

llm2 = ChatOpenAI(model='gpt-4o-mini')
prompt2 = '게임 회사를 창업하려고 하는데, 이름 후보군을 3개 지어주세요'
print(llm.invoke(prompt2))

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
prompt3 = [
    SystemMessage(content="당신은 창의력이 높은 작명가 입니다."),
    HumanMessage(content="게임 회사를 창업하려고 하는데, 이름 후보군을 3개 지어주세요")
]

print(llm.invoke(prompt3))
