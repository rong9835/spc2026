import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template

# 랭체인 기본 불러오기
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# 문서 파서 기본 불러오기 (PyPDFLoader)
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

load_dotenv()
# 1. 백터스토어 셋업
DB_DIR = "./chroma_db"
DATA_DIR = "./DATA"
COLLECTION_NAME = "my_rag_db"

os.makedirs(DATA_DIR, exist_ok=True)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
store = Chroma(collection_name=COLLECTION_NAME, embedding_function=embeddings, persist_directory=DB_DIR)
retriever = store.as_retriever(search_kwargs={"k":3})

# 2. 랭체인 셋업한다 (LCEL)
llm = ChatOpenAI(model="gpt-4o-mini")
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 문서 기반 QA시스템입니다. 아래 문서만 참고해서 답변하시오.\n\n"
               "문서에 적합한 내용이 없으면, '모른다' 라고 답변하시오.\n"
               "문서:\n{context}\n"),
    ("user", "{question}")
])

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


##########
# Flask 
##########
app = Flask(__name__)

@app.get('/')
def index():
    return render_template('index.html')

def add_my_pdf_file(path):
    docs = PyPDFLoader(path).load()
    for d in docs:
        d.metadata["source"] = os.path.basename(path)
    chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100).split_documents(docs)
    # print(chunks)
    store.add_documents(chunks)

@app.post('/upload')
def upload():
    file = request.files.get('file')
    if not file:
        return jsonify({"error":"파일이 없습니다."}), 400

    # 파일이 정상적으로 받아졌으면?? 우리 DATA 폴더에 저장한다.
    path = os.path.join(DATA_DIR, file.filename)
    file.save(path)

    # vectordb에 해당 파일 파싱(청킹)해서 저장하기
    add_my_pdf_file(path)

    return jsonify({"message":"업로드 완료"})

def call_langchain_qa(question):
    if store._collection.count() == 0:
        return "먼저 PDF 문서를 업로드 해 주세요"
    return chain.invoke({"question": question})

@app.post('/ask')
def ask():
    question = request.get_json().get("question")
    print("질문: ", question)

    answer = call_langchain_qa(question)

    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
