# 표준 LCEL 로 RAG 모델을 구현하기

import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

load_dotenv()

# 1. 백터 스토어(DB) 정의하기
DB_DIR="./chroma_db"
COLLECTION_NAME = "my_rag"

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

store = Chroma(collection_name=COLLECTION_NAME, embedding_function=embeddings, persist_directory=DB_DIR)

if store._collection.count() == 0:
    docs = TextLoader("./nvme.txt", encoding="utf-8").load() \
         + TextLoader("./hbm.txt", encoding="utf-8").load()

    chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100).split_documents(docs)
    for c in chunks:
        c.metadata["source"] = os.path.basename(c.metadata.get("source", "?"))

    store.add_documents(chunks)

retriever = store.as_retriever(search_kwargs={"k": 3})


# 2. LLM + 프롬프트 설계하기
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = ChatPromptTemplate.from_messages([
    ("system", 
        "당신은 문서 기반 QA시스템입니다. 아래 문서만 참고해서 답변하시오."
        "문서에 필요한 내용이 없으면 '모른다' 라고 답하시오.\n\n문서:\n{context}"),
    ("user", "{question}")
])


# 3. 표준 질의응답을 위한 파이프라인 설계 (체이닝)
def format_docs(docs):
    return "\n---\n".join(d.page_content for d in docs)

def debug_prompt(prompt):
    print("\n==== LLM에 들어갈 입력값 (즉 PROMPT) ====")
    for msg in prompt.messages:
        print(f"[{msg.type.upper()}]")
        print(msg.content)
    print("\n==== 출력 끝 ====\n")
    return prompt

chain = (
    RunnablePassthrough.assign(context=lambda x: format_docs(retriever.invoke(x["question"])))
    | prompt
    | RunnableLambda(debug_prompt)    # <-- 중간 결과 확인
    | llm
    | StrOutputParser()
)


# 4. 최종 질문
# print(chain.invoke({"question": "NVMe 와 HBM의 차이는??"}))
# print(chain.invoke({"question": "NVMe 와 SSD의 차이는??"}))
print(chain.invoke({"question": "HBM과 NVMe의 제조사는??"}))
