# 목적 - 뉴스를 분석한다.
# 뉴스 입력 -> 요약 
#          -> 감정분석 
#          -> 카테고리 분석
# RunnableParallel

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain_core.runnables import RunnableParallel

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")

# chain 이란? prompt | llm | parser
prompt1 = ChatPromptTemplate.from_template("다음 뉴스를 2~3문장으로 요약해줘.\n\n{news}")
summary_chain = prompt1 | llm | StrOutputParser()

sentiment_chain = (
    ChatPromptTemplate.from_template("다음 뉴스의 전반적 감성을 한 단어로 분석해줘 (긍정 / 부정 / 중립).\n\n{news}")
    | llm
    | StrOutputParser()
)

category_chain = (
    ChatPromptTemplate.from_template("다음 뉴스의 카테고리를 한 단어로 분석해줘 (정치/경제/사회/IT/스포츠/기타).\n\n{news}")
    | llm
    | StrOutputParser()
)

final_chain = RunnableParallel({
    "summary": summary_chain,
    "sentiment": sentiment_chain,
    "category": category_chain
})

news = """
알리바바닷컴이 중소기업(SME)을 위한 에이전틱 AI 비즈니스 팀 ‘Accio Work(액시오 워크)’를 한국 시장에 공식 출시했다. 단순 질의응답형 AI를 넘어 실제 비즈니스 업무를 자율적으로 수행하는 ‘에이전트 투 에이전트(A2A·Agent to Agent)’ 시대를 본격화하겠다는 구상이다.


알리바바닷컴은 28일 롯데호텔 서울에서 ‘액시오 워크 한국 공식 출시 기자간담회’를 열고 시장 조사부터 상품 기획, 글로벌 소싱, 가격 협상, 상품 등록, 마케팅, 스토어 운영까지 전 과정을 AI 에이전트가 수행하는 액시오 워크를 공개했다.


이번에 공개된 액시오 워크의 핵심은 단순 보조 도구 수준을 넘어 실제 업무를 실행하는 ‘플러그 앤 플레이형 AI 에이전트 팀’이라는 점이다. 사용자의 명령을 기다리는 기존 AI 어시스턴트 개념에서 벗어나 목표를 설정하면 AI가 스스로 업무를 수행하고 운영을 지속하는 구조다.


션 양 알리바바닷컴 아시아태평양(APAC) 지역 총괄 본부장은 이날 “AI는 더 이상 미래 기술이 아니라 글로벌 무역 운영 방식을 바꾸는 핵심 인프라가 되고 있다”며 “앞으로 무역 업계는 사람 대 사람 거래를 넘어 에이전트 대 에이전트(A2A) 거래 시대로 진입하게 될 것”이라고 말했다.
"""

result = final_chain.invoke({"news": news})
print(f"원문: {news}")
print(f"요약: {result["summary"]}")
print(f"감성: {result["sentiment"]}")
print(f"카테고리: {result["category"]}")
