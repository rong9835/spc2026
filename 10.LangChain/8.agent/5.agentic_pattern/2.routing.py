from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")
parser = StrOutputParser()


technical_prompt = ChatPromptTemplate.from_template(
"""
당신은 기술 지원 전문가입니다. 정확하고 단계별로 문제를 해결 하는 방법을 안내해 주세요.

고객문의:
{question}

기술 지원 응답:

"""
)

technical_chain = technical_prompt | llm | parser

billing_prompt = ChatPromptTemplate.from_template(
# 고객이 환불 또는 회원탈퇴를 원할경우, 정중하게 사과를 하고, 다른 상품 구매를 유도합니다.
"""
당신은 결제 및 구독 전문 상담원입니다. 사내 정책에 따라 안내하고, 친절하게 응대해주세요.

고객문의:
{question}

결제 지원 응답:

"""
)
billing_chain = billing_prompt | llm | parser

general_prompt = ChatPromptTemplate.from_template(
"""
당신은 친절한 고객 서비스 담당자입니다. 고객의 질문에 대해 친절하게 답변해주세요.

고객문의:
{question}

일반 응답:

"""
)
general_chain = general_prompt | llm | parser

route_map = {
    "technical": technical_chain, # 기술적인 질문에 답변하는 체인
    "billing": billing_chain, # 결제관련 질문에 답변하는 체인
    "general": general_chain, # 그외 기타 나머지 일번적인 질문
}


classifier_prompt = ChatPromptTemplate.from_template(
"""
다음 고객 문의를 보고, 어느 카테고리에 해당하는지 분류해 주세요. 반드시 아래 카테고리중 하나로만 출력해주세요.

카테고리 선택 항목: technical, billing, general

고객 문의: {question}

카테고리: 
"""
)
classifier_chain = classifier_prompt | llm | parser

# 사용자의 질문을 받아 적절한 챗봇으로 라우팅한다.
def route_query(input: dict) -> str:
    question = input["question"]

    # 1단계. 분류를 시켜서 카테고리를 가져온다.
    category = classifier_chain.invoke({"question": question}).strip().lower()
    print(f"분류 결과: {category}")

    # 2단계. 해당 카테고리 체인을 다시 호출한다.
    chain = route_map.get(category, general_chain)
    response = chain.invoke({"question": question})

    return f"[{category.upper()}] {response}"


routing_chain = RunnableLambda(route_query)

# 결과 확인
test_questions = [
    "프로그램이 자꾸 충돌하는데 어떻게 해야 하나요?",
    "구독을 취소하고 환불받고 싶습니다.",
    "이 서비스에서는 어떤 기능을 제공하나요?",
    "API 연동 시 인증 오류가 발생합니다."
]

for i, question in enumerate(test_questions, 1):
    print(f"\n--------------")
    print(f"질문 {i}: {question}")
    result = routing_chain.invoke({"question": question})
    print(f"응답: {result}")
