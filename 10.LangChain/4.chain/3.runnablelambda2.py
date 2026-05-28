from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, CommaSeparatedListOutputParser
from langchain_core.runnables import RunnableLambda

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")

prompt_name = ChatPromptTemplate.from_template(
    "{product} 을/를 만드는 회사의 이름을 하나 추천해주세요. 이름만 답하시오."
)
prompt_slogan = ChatPromptTemplate.from_template(
    "{company_name} 회사의 캐치프레이즈를 만들어주세요. 캐치프레이즈만 답하시오."
)

chain1 = (
    # 사용자 입력 처리
    prompt_name 
    | llm 
    | StrOutputParser() 
    | RunnableLambda(lambda name: {"company_name": name.strip()}) 

    # 두번째 체인
    | prompt_slogan 
    | llm 
    | StrOutputParser()
    | RunnableLambda(lambda slogan: {"slogan": slogan.strip()})
)

chain2 = (
    # 사용자 입력 처리
    prompt_name 
    | llm 
    | StrOutputParser() 
    | RunnableLambda(lambda name: {"company_name": name.strip()}) 

    # 두번째 체인
    | RunnableLambda(lambda d: {
        "company_name": d["company_name"],
        "slogan ": (
            prompt_slogan 
            | llm 
            | StrOutputParser()
        ).invoke({
            "company_name": d["company_name"]
        })
    })
    
)

# result = chain1.invoke({"product": "친환경 에코백"})
result = chain2.invoke({"product": "친환경 에코백"})
print(f"결과: {result}")
