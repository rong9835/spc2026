# pip install langchain langchain-openai

import os
from dotenv import load_dotenv

# from langahin.llms import OpenAI   # 구버전... 
from langchain_openai import OpenAI  # 시버전....

load_dotenv()

llm = OpenAI(model="gpt-4o-mini")
# print(llm)

prompt = "오늘 저녁은 무엇을 먹을까요?"
result = llm.invoke(prompt)
print(result)
