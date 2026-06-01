import os
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

load_dotenv()

DB_DIR = "./chroma_db"

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

def build_document(file_path, collection):
    store = Chroma(collection_name=collection, embedding_function=embeddings, persist_directory=DB_DIR)
    if store._collection.count() > 0:  # 지금은 단순 DB라서, 최초 1회만 빌드...
        return store
    
    docs = TextLoader(file_path, encoding="utf-8").load()
    chunks = splitter.split_documents(docs)
    print(chunks)
    for c in chunks:
        c.metadata["source"] = os.path.basename(file_path)

    return Chroma.from_documents(chunks, embeddings, collection_name=collection, persist_directory=DB_DIR)

# 1. 컬렉션 두개 준비
collections = {
    "nvme": build_document("./nvme.txt", "nvme"),
    "hbm": build_document("./hbm.txt", "hbm"),
}
for name, store in collections.items():
    print(f"컬렉션: {name}, 청크개수: {store._collection.count()}")

# 2. 컬랙션 내 검색
def search_in(name, query, k=2):
    return collections[name].similarity_search(query, k=k)

def search_all(query, k_per=2):
    results = []
    for name, store in collections.items():
        for doc in store.similarity_search(query, k=k_per):
            doc.metadata["collection"] = name # 어느 컬랙션에서 가져왔는지 기록
            results.append(doc)
    return results

query = "PCIe 인터페이스 속도는?"
print("\n질문: ", query)
print("\n=== 'nvme' 컬렉션에서 이걸 물어보면? ===")
for d in search_in('nvme', query):
    # print(f" -> {d.page_content[:50]}...")
    print(f" -> {d.page_content}")

print("\n=== 'nvme, hbm' 등 있는 컬렉션에 이걸 다 물어보려면? ===")
for d in search_all(query):
    print(f" -> [{d.metadata['collection']}] {d.page_content}")
