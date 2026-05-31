import os
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_chroma import Chroma

load_dotenv()

embeddings = OpenAIEmbeddings(model='text-embedding-3-small')
llm = ChatOpenAI(model='gpt-4o-mini')
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

# ─────────────────────────────────────────────
# 숙제 3: TXT 로더 - hbm.txt
# ─────────────────────────────────────────────
hbm_docs = TextLoader('./hbm.txt', encoding='utf-8').load()
print(f'hbm 로딩 완료: {len(hbm_docs)}개')

# ─────────────────────────────────────────────
# 숙제 4: TXT 로더 - nvme.txt
# ─────────────────────────────────────────────
nvme_docs = TextLoader('./nvme.txt', encoding='utf-8').load()
print(f'nvme 로딩완료 {len(nvme_docs)}개')


# ─────────────────────────────────────────────
# 숙제 5: 두 개 합쳐서 비교 질문 답변
# ─────────────────────────────────────────────
both_chunks = splitter.split_documents(hbm_docs + nvme_docs)
store = Chroma.from_documents(both_chunks, embeddings, collection_name="both")

retriever = store.as_retriever(search_kwargs={"k": 3})

prompt = ChatPromptTemplate.from_messages([
    ("system",
        "당신은 문서 기반 Q&A 시스템입니다. 아래 문서만을 참고해서 답하세요."
        "문서에 적합한 내용이 없으면, '모른다' 라고 답변하세요.\n\n문서:\n{context}"),
    ("user", "{question}")
])

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

chain = (
    RunnablePassthrough.assign(context=lambda x: format_docs(retriever.invoke(x["question"])))
    | prompt
    | llm
    | StrOutputParser()
)

print("\n[숙제5] 비교 질문:")
print(chain.invoke({"question": "HBM과 NVMe의 차이점은 무엇인가요?"}))

# ─────────────────────────────────────────────
# 숙제 6: PDF 로더
# ─────────────────────────────────────────────
pdf_pages = PyPDFLoader("./Javascript_Secure_Coding.pdf").load()
print(f"\n[숙제6] PDF 로딩 완료: {len(pdf_pages)}페이지")

# ─────────────────────────────────────────────
# 숙제 7: 컬렉션 분리 vs 합치기 실험
# ─────────────────────────────────────────────
hbm_store  = Chroma.from_documents(splitter.split_documents(hbm_docs),  embeddings, collection_name="hbm_only")
nvme_store = Chroma.from_documents(splitter.split_documents(nvme_docs), embeddings, collection_name="nvme_only")

def ask(store, question):
    retriever = store.as_retriever(search_kwargs={"k": 3})
    chain = (
        RunnablePassthrough.assign(context=lambda x: format_docs(retriever.invoke(x["question"])))
        | prompt | llm | StrOutputParser()
    )
    return chain.invoke({"question": question})

print("\n[숙제7] 분리 실험:")
print("HBM 컬렉션에 NVMe 질문 →", ask(hbm_store,  "NVMe의 속도는 어떻게 되나요?"))
print("NVMe 컬렉션에 HBM 질문 →", ask(nvme_store, "HBM의 대역폭은 어떻게 되나요?"))

print("\n[숙제7] 합치기 실험:")
print("합친 컬렉션에 비교 질문 →", ask(store, "HBM과 NVMe 중 어느 것이 더 빠른가요?"))
