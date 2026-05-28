# 목적: 긴 문장을 받아서 짧게 요약한다.

from dotenv import load_dotenv

from langchain_core.prompts import (
    ChatPromptTemplate, 
    HumanMessagePromptTemplate, 
    SystemMessagePromptTemplate, 
    AIMessagePromptTemplate
)

from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda

load_dotenv()

template = "다음의 긴 내용을 3개의 문장으로 요약하시오:\n\n{article}"
chat_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("당신은 전문 문장 요약가 입니다."),
    HumanMessagePromptTemplate.from_template(template)
])

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)  # 이런 경우 0.3~0.5 정도를 쓴다.

chain = chat_prompt | llm | RunnableLambda(lambda x: {"summary": x.content.strip()})

input_text = {
    "article": "방송미디어통신위원회는 정보통신정책연구원(KISDI)와 함께 2025년 지능정보사회 이용자 패널조사 결과 전체 응답자의 38.9%가 생성형 AI를 이용한 경험이 있는 것으로 나타났다고 28일 밝혔다."
               "지난 2024년에는 생성형AI 이용자 비중이 24.0%였고, 2023년에는 12.3% 였는데, 3년 연속 이용자 비중이 큰 폭으로 늘고 있는 것이다."
               "AI 이용자들의 하루 평균 이용 시간은 49.6분에 달하는 것으로 나타났다."
               "과학기술정보통신부의 '2025 인터넷 이용실태조사' 결과 우리 국민들이 주 평균 21.6시간, 하루 평균 3.1시간 인터넷을 사용하는 것을 감안하면, 전체 인터넷 사용 시간의 26.7%가 AI 사용 시간인 것으로 풀이된다."
}

result = chain.invoke(input_text)
print("요약 결과: ", result["summary"])
