# pip install pypdf
# 이거 외에도 다양한 pdf 로더가 있음.. fitz 라는것도 유명함..

from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("./Javascript_Secure_Coding.pdf")
pages = loader.load()

print(f"PDF 페이지수: {len(pages)}\n")

for p in pages:
    if p.page_content.strip():
        print(f"발견한 내용이 있는 첫페이지의 metadata:\n{p.metadata}")
        print(f"페이지내용 (앞 400글자):\n{p.page_content[:400]}...")
        break
