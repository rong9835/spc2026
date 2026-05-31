# pip install chromadb
# pip install langchain-chroma

import os
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from langchain_chroma import Chroma

load_dotenv()

# DB를 저장할 폴더 경로, 컬렉션(테이블) 이름
DB_DIR = "./chroma_db"
COLLECTION_NAME = "memory"

# 텍스트를 숫자(벡터)로 변환하는 도구
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

def build_store():
    # hbm.txt 파일 읽기
    docs = TextLoader("./hbm.txt", encoding="utf-8").load()
    # 읽은 내용을 500글자씩 청크로 자르기 (overlap=100: 앞뒤 100글자 겹치게)
    chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100).split_documents(docs)
    # 청크들을 숫자로 변환해서 Chroma DB에 저장
    store = Chroma.from_documents(
        chunks, embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=DB_DIR  # 이 폴더에 파일로 저장됨 (껐다 켜도 유지)
    )
    return store

def load_store():
    # 이미 저장된 DB를 불러오기 (새로 만들지 않음 → 비용 절약)
    store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=DB_DIR
    )
    print(f"기존 DB 로딩 성공 - {store._collection.count()} 청크 로딩됨")
    return store

# DB 폴더가 이미 있으면 불러오고, 없으면 새로 만들기
if os.path.exists(DB_DIR) and os.listdir(DB_DIR):
    store = load_store()
else:
    store = build_store()

# retriever: 질문이 들어오면 관련 청크 k개를 DB에서 찾아주는 검색기
retriever = store.as_retriever(search_kwargs={"k": 3})

# 답변해줄 GPT 모델
llm = ChatOpenAI(model="gpt-4o-mini")

# AI한테 줄 지시문 (system = AI 역할 설정, user = 실제 질문)
prompt = ChatPromptTemplate.from_messages([
    ("system",
        "당신은 문서 기반 Q&A 시스템입니다. 아래 문서만을 참고해서 답하세요."
        "문서에 적합한 내용이 없으면, '모른다' 라고 답변하세요.\n\n문서:\n{context}"),
    ("user", "{question}")
])

# 찾아온 청크 여러 개를 하나의 텍스트로 합치는 함수
def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

# 전체 흐름: 질문 → 관련 청크 검색 → 프롬프트 조립 → GPT 답변 → 텍스트 출력
chain = (
    RunnablePassthrough.assign(context=lambda x: format_docs(retriever.invoke(x["question"])))
    | prompt   # 검색된 내용 + 질문을 프롬프트에 넣기
    | llm      # GPT한테 답변 요청
    | StrOutputParser()  # GPT 응답을 깔끔한 문자열로 변환
)

print(chain.invoke({"question": "HBM의 성능은 어떤가요?"}))
print('-' * 60)
print(chain.invoke({"question": "NVMe와 HBM은 다른건가요?"}))
