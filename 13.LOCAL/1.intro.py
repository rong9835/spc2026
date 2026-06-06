# pip install ollama

import ollama

ollama.pull("mistral")
response = ollama.chat(model="mistral", messages=[
    {"role": "user", "content": "인공지능에 대해서 설명해줘"}
])

print(response["message"]["content"])
