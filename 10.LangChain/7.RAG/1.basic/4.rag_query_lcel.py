from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

docs = [
    Document(page_content="NVMe 는 SSD 의 인터페이스 규격으로 PCIe를 사용한다."),
    Document(page_content="SATA SSD는 NVMe 보다 속도가 느리다."),
    Document(page_content="HDD는 회전 디스크 기반이라 IO가 느린 편이다."),
    Document(page_content="파이썬은 인기 있는 프로그래밍 언어다."),
    Document(page_content="자바스크립트는 브라우저에서 동작하는 언어이다."),
    Document(page_content="Rust는 메모리 안정성과 성능을 동시에 추구한다."),
]

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
store = InMemoryVectorStore.from_documents(docs, embedding=embeddings)
retriever = store.as_retriever(search_kwargs={"k": 3})

prompt = ChatPromptTemplate.from_template("""
아래 문서만을 참고하여 질문에 답하시오.\n\n        
문서:\n{context}\n\n                                         
질문:{question}
""")

def format_docs(docs):
    """ 검색된 Document 리스트를 -> 하나의 문자열로 변환한다 """
    return "\n\n".join(d.page_content for d in docs)

# [Document(...), Document(...), Document(...)] => 
# HDD는 회전 디스크 기반이라 IO가 느린 편이다.
#
# 파이썬은 인기 있는 프로그래밍 언어다.
# ...

chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough()  # 질문을 다음 파이프라인으로도 그대로 전달함.
    }
    | prompt
    | llm
    | StrOutputParser()
)

# question = "NVMe 와 SATA의 차이는 무엇인가요?"
# question = "파이썬은 어떤 언어인가요?"
question = "파인애플은 어떤 과일인가요?"
print(f"사용자질문: {question}")
print(f"챗봇의응답: {chain.invoke(question)}")
