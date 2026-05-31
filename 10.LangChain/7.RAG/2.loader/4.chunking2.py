from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

loader = PyPDFLoader("./Javascript_Secure_Coding.pdf")
pages = loader.load()

print(f"PDF 페이지수: {len(pages)}\n")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=500
)

chunks = splitter.split_documents(pages)
print(f"청킹 후 문서 갯수: {len(chunks)}\n")

first = chunks[0]
print(first.metadata)
print(first.page_content)
print('-' * 60)

first = chunks[50]
print(first.metadata)
print(first.page_content)
