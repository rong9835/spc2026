from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, CommaSeparatedListOutputParser

load_dotenv()

prompt1 = ChatPromptTemplate.from_template(
    "{product}을/를 만드는 회사의 이름을 하나 추천해주세요."
)

llm = ChatOpenAI(model="gpt-4o-mini")

chain1 = prompt1 | llm | StrOutputParser()
result1 = chain1.invoke({"product": "웹게임"})

print(f"타입: {type(result1)}")  # <class 'str'>
print(f"결과: {result1}")

prompt2 = ChatPromptTemplate.from_template(
    "{topic}에 관련된 키워드를 5개만 쉼표로 구분해서 나열해주세요."
)
chain2 = prompt2 | llm | CommaSeparatedListOutputParser()
result2 = chain2.invoke({"topic": "인공지능"})

print(f"타입: {type(result2)}")  # <class 'list'>
print(f"결과: {result2}")

print('-'*30)
######################################
# 위 두개의 다른 체인들을 LCEL로 하나로 합쳐보기
######################################
prompt_name = ChatPromptTemplate.from_template(
    "{product} 을/를 만드는 회사의 이름을 하나 추천해주세요. 이름만 답하시오."
)
prompt_slogan = ChatPromptTemplate.from_template(
    "{company_name} 회사의 캐치프레이즈를 만들어주세요. 캐치프레이즈만 답하시오."
)

chain3 = (
    prompt_name 
    | llm 
    | StrOutputParser() 
    | (lambda name: {"company_name": name.strip()}) 
    | prompt_slogan 
    | llm 
    | StrOutputParser()
)

result3 = chain3.invoke({"product": "친환경 에코백"})
print(f"결과: {result3}")
