# 7. RAG (Retrieval Augmented Generation) 핵심 요약

> **RAG란?** AI가 내가 가진 문서를 참고해서 답변하게 만드는 기술  
> **비유:** 시험 볼 때 교과서를 옆에 놓고 답 찾아보는 것처럼, AI도 문서를 찾아보고 답한다

---

## 전체 흐름 한눈에 보기

```
내 문서(PDF, TXT)
    ↓ 잘게 자르기 (청킹)
    ↓ 숫자로 변환 (임베딩)
    ↓ 저장 (벡터 DB)
    
사용자 질문
    ↓ 질문도 숫자로 변환
    ↓ 비슷한 문서 조각 찾기 (검색)
    ↓ 문서 + 질문을 AI에게 전달
    ↓ AI가 문서를 참고해서 답변
```

---

## 폴더 구조

```
7.RAG/
├── 1.basic/        ← RAG 기초 개념 (임베딩, 벡터, 첫 RAG)
├── 2.loader/       ← 파일 불러오기 + ChromaDB 저장
├── 3.store/        ← 여러 파일 관리 방법
├── 4.langchain/    ← 완성형 RAG + 출처 표시
└── 9.WEB/          ← 웹 애플리케이션으로 만들기
```

---

## 1단계: basic — RAG의 핵심 원리

### 임베딩이란? (`1.embedding.py`)

> **비유:** 단어를 지도 위의 점으로 찍는 것  
> 비슷한 의미의 문장은 지도에서 가까운 곳에 찍힌다

```python
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 문장 하나 → 1536개의 숫자로 변환 (1536차원 벡터)
vec = embeddings.embed_query("고양이가 소파 위에서 잔다.")

# 두 벡터가 얼마나 가까운지 측정 (코사인 유사도)
# 1.0 = 완전히 같음, 0.0 = 전혀 관련 없음
```

**핵심:** "고양이가 소파에서 잔다" ↔ "강아지가 침대에서 잔다" → 유사도 높음  
"고양이가 소파에서 잔다" ↔ "파이썬은 프로그래밍 언어다" → 유사도 낮음

---

### 벡터 저장소 (`2.inmemoryvector.py`)

> **비유:** 유사도로 정렬되는 스마트 서랍장  
> 질문을 넣으면 가장 관련 있는 문서를 꺼내준다

```python
# 문서들을 저장
store = InMemoryVectorStore.from_documents(docs, embedding=embeddings)

# 질문과 가장 비슷한 문서 3개 찾기
results = store.similarity_search("NVMe와 SATA의 차이?", k=3)
```

**InMemoryVectorStore** = 메모리에만 저장 (프로그램 끄면 사라짐)

---

### 첫 번째 RAG (`3.first_rag.py`)

> 검색 → AI 답변의 가장 단순한 형태

```
1. 질문과 비슷한 문서 3개 검색
2. 문서 내용 + 질문을 프롬프트에 합치기
3. AI에게 "이 문서를 참고해서 답해줘" 요청
4. 답변 출력
```

---

### LCEL 파이프라인 (`4.rag_query_lcel.py`)

> **비유:** 공장 컨베이어 벨트처럼 각 단계를 연결

```python
chain = (
    {
        "context": retriever | format_docs,   # 검색 → 텍스트 변환
        "question": RunnablePassthrough()     # 질문 그대로 전달
    }
    | prompt    # 프롬프트 완성
    | llm       # AI 답변
    | StrOutputParser()  # 텍스트로 변환
)

chain.invoke("NVMe와 SATA의 차이는?")
```

**LCEL의 `|` (파이프)**: 앞 단계 결과를 다음 단계 입력으로 자동 연결

**중요 개념 `RunnablePassthrough`**: 질문을 변형 없이 그대로 다음 단계로 전달

---

## 2단계: loader — 실제 파일 불러와서 저장하기

### 파일 불러오기 (`1.text_loader.py`, `2.pdf_loader.py`)

```python
# 텍스트 파일 로딩
loader = TextLoader("./hbm.txt", encoding="utf-8")
documents = loader.load()
# → documents[0].page_content  : 파일 내용 전체
# → documents[0].metadata      : {"source": "./hbm.txt"}

# PDF 파일 로딩 (페이지별로 분리됨)
loader = PyPDFLoader("./파일.pdf")
pages = loader.load()  # 각 페이지가 하나의 Document
```

---

### 청킹 — 문서를 잘게 자르기 (`3.chunking.py`, `4.chunking2.py`)

> **왜 자르나?** AI는 한 번에 읽을 수 있는 텍스트 양이 제한됨  
> **비유:** 긴 책을 형광펜 칠한 핵심 단락들로 나누는 것

```python
# 방법 1: 문자 기준으로 자르기
char_splitter = CharacterTextSplitter(
    separator="\n\n",   # 빈 줄을 기준으로 나누되
    chunk_size=500,     # 최대 500글자
    chunk_overlap=100   # 앞뒤 100글자 겹치게 (내용 연속성 유지)
)

# 방법 2: 재귀적으로 자르기 (더 스마트함, 보통 이걸 씀)
recur_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)
```

| 설정 | 의미 |
|------|------|
| `chunk_size=500` | 조각 하나의 최대 크기 (500글자) |
| `chunk_overlap=100` | 이전 조각과 100글자 겹침 (문장이 중간에 잘려도 의미 유지) |
| 권장 비율 | 1000:200, 1500:300, 2000:500 |

---

### ChromaDB — 영구 저장 벡터 DB (`5.vectorstore.py`, `6.vectorstore2.py`)

> **InMemoryVectorStore vs ChromaDB**  
> 메모리 저장 = 임시 (프로그램 종료 시 삭제)  
> ChromaDB = 파일에 영구 저장 (폴더에 `chroma_db` 생성)

```python
# 최초 한 번만: DB 생성 후 저장
store = Chroma.from_documents(
    chunks, embeddings,
    collection_name="memory",    # DB 안의 "테이블" 이름
    persist_directory="./chroma_db"  # 저장 폴더
)

# 이후: 기존 DB 불러오기
store = Chroma(
    collection_name="memory",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)
```

**스마트 패턴:**
```python
if os.path.exists(DB_DIR) and os.listdir(DB_DIR):
    store = load_store()   # 있으면 불러오기
else:
    store = build_store()  # 없으면 새로 만들기
```

---

### Chroma + LLM 연결 (`7.rag_query.py`)

```python
retriever = store.as_retriever(search_kwargs={"k": 3})

chain = (
    RunnablePassthrough.assign(
        context=lambda x: format_docs(retriever.invoke(x["question"]))
    )
    | prompt | llm | StrOutputParser()
)

chain.invoke({"question": "HBM의 성능은?"})
```

---

## 3단계: store — 여러 파일 체계적으로 관리하기

### 방법 1: 컬렉션 여러 개 (`1.multi_collection.py`)

> **비유:** 주제별로 서랍을 나누는 것 (반도체 서랍, 프로그래밍 서랍)

```python
collections = {
    "nvme": build_document("./nvme.txt", "nvme"),  # NVMe 전용 DB
    "hbm": build_document("./hbm.txt", "hbm"),    # HBM 전용 DB
}

# 특정 컬렉션에서만 검색
search_in('nvme', "PCIe 속도는?")

# 모든 컬렉션에서 동시에 검색
search_all("PCIe 속도는?")
```

---

### 방법 2: 하나의 컬렉션에 메타데이터로 구분 (`2.multi_source_single_collection.py`)

> **비유:** 하나의 서랍에 색깔 라벨 붙여서 관리

```python
# 여러 파일을 하나의 DB에 통합
FILES = ["./nvme.txt", "./hbm.txt", "cisc2024.pdf"]

for c in chunks:
    c.metadata["source"] = os.path.basename(path)  # 출처 라벨 붙이기

store = Chroma.from_documents(chunks, ..., collection_name="unified")

# 특정 파일만 필터링해서 검색
store.similarity_search(query, k=2, filter={"source": "hbm.txt"})
```

| 방식 | 장점 | 단점 |
|------|------|------|
| 멀티 컬렉션 | 완전 분리, 주제별 관리 쉬움 | 전체 검색 시 코드 복잡 |
| 단일 컬렉션 | 코드 단순, 전체 검색 쉬움 | 필터링 로직 필요 |

---

## 4단계: langchain — 완성형 RAG

### 표준 RAG 구현 (`1.total.py`)

```python
# debug_prompt로 AI에게 실제 전달되는 내용 확인 가능
def debug_prompt(prompt):
    for msg in prompt.messages:
        print(f"[{msg.type.upper()}]")
        print(msg.content)
    return prompt

chain = (
    RunnablePassthrough.assign(context=...)
    | prompt
    | RunnableLambda(debug_prompt)   # 중간 확인용
    | llm
    | StrOutputParser()
)
```

---

### 출처 표시 추가 (`2.reference.py`)

> **핵심 기능:** 답변에 어떤 파일에서 가져왔는지 표시

```python
def extract_sources(docs):     # 중복 없이 출처 파일명 추출
    seen, sources = set(), []
    for d in docs:
        src = d.metadata.get("source", "N/A")
        if src not in seen:
            seen.add(src)
            sources.append(src)
    return sources

def append_sources(d):         # 답변 끝에 출처 붙이기
    src_lines = "\n".join(f" - {s}" for s in d["sources"])
    return f"{d['answer']}\n\n 참고문서: \n{src_lines}"
```

**출력 예시:**
```
NVMe는 PCIe를 사용하며 SATA보다 훨씬 빠릅니다...

 참고문서:
 - nvme.txt
 - hbm.txt
```

---

## 5단계: WEB — 웹 애플리케이션으로 만들기

### 기본 웹앱 (`9.WEB/1.simple/app.py`)

> PDF 업로드 → 질문 → 답변을 웹 브라우저에서

```
[브라우저]
    ↓ POST /upload  (PDF 파일 전송)
    → 서버에 파일 저장 + ChromaDB에 청킹 저장
    
    ↓ POST /ask  (질문 전송 {"question": "..."})
    → RAG 체인 실행
    → {"answer": "답변 내용"} 반환
```

**Flask API 구조:**
```python
@app.get('/')           # 메인 페이지
@app.post('/upload')    # PDF 업로드 → ChromaDB 저장
@app.post('/ask')       # 질문 → RAG 답변
```

---

### 파일 삭제 기능 추가 (`9.WEB/2.delete/app.py`)

```python
@app.delete('/files/<path:source>')  # 파일 삭제
def remote_file(source):
    delete_document(source)
    return jsonify({"message": "삭제 완료"})

@app.get("/files")   # 업로드된 파일 목록 조회
def files():
    return jsonify({"files": list_documents()})
```

**삭제 로직:**
```python
def delete_document(source):
    # 1. ChromaDB에서 해당 파일의 모든 청크 삭제
    store._collection.delete(where={"source": source})
    # 2. 실제 파일도 삭제
    os.remove(os.path.join(DATA_DIR, source))
```

---

## 핵심 개념 정리

| 용어 | 쉬운 설명 |
|------|-----------|
| **임베딩** | 텍스트 → 숫자 벡터로 변환 (의미를 수학으로 표현) |
| **벡터 DB** | 숫자 벡터를 저장하고 유사한 것을 빠르게 찾는 DB |
| **청킹** | 긴 문서를 AI가 소화할 수 있는 크기로 자르기 |
| **retriever** | 질문과 비슷한 문서 조각을 찾아오는 검색기 |
| **LCEL** | LangChain 파이프라인 문법 (`|`로 단계 연결) |
| **ChromaDB** | 로컬 파일에 저장하는 벡터 DB (무료, 설치 간단) |
| **컬렉션** | ChromaDB 안의 테이블 (주제별로 분리 가능) |
| **메타데이터** | 문서 조각에 붙이는 라벨 (어느 파일 출신인지 등) |

---

## 학습 경로 요약

```
1.basic  →  임베딩과 유사도의 원리 이해
    ↓
2.loader →  실제 파일을 ChromaDB에 영구 저장
    ↓
3.store  →  여러 파일을 체계적으로 관리
    ↓
4.langchain → 출처 표시 등 완성도 높이기
    ↓
9.WEB    →  웹 애플리케이션으로 배포
```
