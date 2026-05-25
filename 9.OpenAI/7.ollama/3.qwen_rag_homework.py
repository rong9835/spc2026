from dotenv import load_dotenv
import os

from openai import OpenAI

import faiss
import numpy as np

import requests

MODEL_NAME = "qwen2.5:1.5b"

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

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
    return np.array(response.data[0].embedding)

index = faiss.IndexFlatL2(1536)
doc_embeddings = np.array([get_embedding(doc) for doc in documents])
index.add(doc_embeddings)

def ask_qwen(question):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": MODEL_NAME,
            "prompt": question,
            "stream": False
        }
    )
    data = response.json()
    return data['response']

def rag_query(user_query):
    query_embedding = get_embedding(user_query)
    distance, indices = index.search(np.array([query_embedding]), k=1)
    retrieved_doc = documents[indices[0][0]]

    true_distance = np.sqrt(distance[0][0])
    similarity_score = 1 / (1 + true_distance)

    if similarity_score < 0.60:
        return "해당 내용은 적합한 답변을 찾을 수 없습니다."

    prompt = f"""
        아래 질문을 보고 답변하시오. 관련 자료만을 참고해서 답변하고, 엉뚱한 자료일 경우 추가적인 답변 없이 모른다고 하시오.

        [사용자 질문]
        {user_query}

        [관련자료]
        {retrieved_doc}
    """

    return ask_qwen(prompt)

print("RAG 챗봇을 시작합니다. 종료하려면 'exit'를 입력하세요.")

while True:
    user_input = input("\n나: ")
    if user_input == "exit":
        print("종료합니다.")
        break

    print("응답:", rag_query(user_input))
