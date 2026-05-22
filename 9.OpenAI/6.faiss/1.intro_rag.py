# pip install faiss-cpu

from dotenv import load_dotenv
import os

from openai import OpenAI

import faiss
import numpy as np

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 우리의 문장 데이터
documents = [
    "한국소프트웨어저작권협회는 SPC라는 약자를 가지고 있고, 다양한 국내 기업의 SW라이선스와 저작권을 다루는 곳입니다.",
    "홍길동은 2020년 1월 1일 생으로, 강원도 설빙산에서 태어났고, 그곳에서 호랑이를 잡아먹으며 성장하였습니다.",
    "Python 은 개발 언어중에 가장 쉽다고 하는데, 그렇게 쉬운 언어는 아닙니다."
]

def get_embedding(text):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    # print(response)
    return np.array(response.data[0].embedding)

# print(get_embedding(documents))
index = faiss.IndexFlatL2(1536)    # OpenAI 로 임베딩 하면 1536차원
doc_embeddings = np.array([get_embedding(doc) for doc in documents])
index.add(doc_embeddings)  # 나온 숫자값을 백터DB에 넣는다

# 사용자의 질문을 받아서 우리의 백터DB에 물어본다
def rag_query(user_query):
    query_embedding = get_embedding(user_query)
    print(query_embedding)
    _, indices = index.search(np.array([query_embedding]), k=1)  # 백터DB에서 질문(user_query)의 숫자값 과 가장 가까운거 k=1 개를 반환하시오.
    retrieved_doc = documents[indices[0][0]]

    prompt = f"""
너는 검색 기반 RAG 응답 시스템이다.

[응답 규칙]
1. 반드시 관련자료에 근거해서만 답변하라.
2. 질문과 관련자료의 연관성이 낮거나 답변 근거가 부족하면:
   - 정중하게 답변이 어렵다고 말하라.
   - 이유를 짧게 설명하라.
   - 매번 표현을 조금씩 다르게 작성하라.
   - 가벼운 이모티콘을 사용할 수 있다.
3. 질문과 무관한 내용을 추론하거나 지어내지 마라.
4. 관련자료 자체를 언급하지 마라.
   - 예: "제공된 자료에 따르면", "문서상", "컨텍스트에 따르면" 등의 표현 금지
5. 답변은 간결하고 자연스러운 한국어로 작성하라.

[사용자 질문]
{user_query}

[관련자료]
{retrieved_doc}
    """

    print(">>>>>")
    print("우리가 실제로 gpt에게 물어보는 내용\n", prompt)
    print("<<<<<")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 친절한 AI도우미 입니다."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# query = "홍길동은 누구인가요?"
# query = "저작권협회는 누구인가요?"
# query = "파이썬은 어떤 언어인가요?"
query = "오늘 저녁은 뭐 먹을까??"

print(rag_query(query))
