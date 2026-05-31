from langchain_community.document_loaders import TextLoader

loader = TextLoader("./hbm.txt", encoding="utf-8")
documents = loader.load()

print(f"불러온 문서의 갯수: {len(documents)}")

doc = documents[0]
print(f"page_content (앞 100글자):\n{doc.page_content[:100]}...\n")
print(f"metadata: {doc.metadata}")
