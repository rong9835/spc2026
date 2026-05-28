from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnableParallel

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")

base_prompt = ChatPromptTemplate.from_messages([
    ("system", "다음 한국어를 {language} 로 번역하시오."),
    ("human", "{text}")
])

chain_en = (
    base_prompt.partial(language="English")
    | llm
    | RunnableLambda(lambda x: x.content.strip())
)

chain_ch = (
    base_prompt.partial(language="Chinese")
    | llm
    | RunnableLambda(lambda x: x.content.strip())
)

chain_ja = (
    base_prompt.partial(language="Japanese")
    | llm
    | RunnableLambda(lambda x: x.content.strip())
)

chain_fr = (
    base_prompt.partial(language="Franch")
    | llm
    | RunnableLambda(lambda x: x.content.strip())
)

parallel_chain = RunnableParallel({
    "english": chain_en,
    "chinese": chain_ch,
    "japanese": chain_ja,
    "franch": chain_fr
})

result = parallel_chain.invoke({
    "text": "안녕하세요, 만나서 반갑습니다."
})

print(result)
