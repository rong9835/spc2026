# pip install faiss-cpu

from dotenv import load_dotenv
import os

from openai import OpenAI

import faiss
import numpy as np

import requests

MODEL_NAME = "qwen2.5:1.5b"

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

def ask_qwen(question):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json= {
            "model": MODEL_NAME,
            "prompt": question,
            "stream": False
        }
    )

    data = response.json()
    return data['response']

# 사용자의 질문을 받아서 우리의 백터DB에 물어본다
def rag_query(user_query):
    query_embedding = get_embedding(user_query)
    print(query_embedding)
    distance, indices = index.search(np.array([query_embedding]), k=1)  # 백터DB에서 질문(user_query)의 숫자값 과 가장 가까운거 k=1 개를 반환하시오.
    retrieved_doc = documents[indices[0][0]]

    # 거리측정된걸 유사도 점수로 변환
    true_distance = np.sqrt(distance[0][0])
    similarity_score = 1 / (1 + true_distance)   # 거리값을 정규화하여 유사도 점수로 변환

    print("\n===\n유사도점수")
    print(f"사용자 질문: {user_query}")
    print(f"검색된 문서: {retrieved_doc}")
    print(f"유사도 점수: {similarity_score:.3f}")

    if similarity_score < 0.60:
        return "해당 내용은 적합한 답변을 찾을수 없습니다."

    prompt = f"""
        아래 질문을 보고 답변하시오. 관련 자료만을 참고해서 답변하고, 엉뚱한 자료일 경우 추가적인 답변 없이 모른다고 하시오.

        [사용자 질문]
        {user_query}

        [관련자료]
        {retrieved_doc}
    """

    print(">>>>>")
    print(f"질문과 가까운 백터 인덱스: {indices}, 그 거리: {distance}")
    print("<<<<<")

    return ask_qwen(prompt)

# query = "홍길동은 누구인가요?"
query = "저작권협회는 누구인가요?"
# query = "파이썬은 어떤 언어인가요?"
# query = "오늘 저녁은 뭐 먹을까??"
# query = "JavScript 은 개발 언어중에 가장 쉽다고 하는데, 그렇게 쉬운 언어는 아닙니다."
# query = "요즘 인기있는 영화는 무엇인가요?"

print(rag_query(query))
