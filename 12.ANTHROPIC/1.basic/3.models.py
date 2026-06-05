import anthropic
from dotenv import load_dotenv
import time

load_dotenv()

client = anthropic.Anthropic()

models = ['claude-haiku-4-5', 'claude-sonnet-4-6', 'claude-opus-4-7', 'claude-opus-4-8']

prompt = "인공지능과 LLM 의 동작 원리를 초등학생도 이해할수 있도록 쉽게 설명해줘"

for model in models:
    start = time.time()
    msg = client.messages.create(
        model=model,
        max_tokens=500,
        messages=[{"role":"user", "content": prompt}]
    )
    elasped = time.time() - start
    text = msg.content[0].text
    print(f"[{model}] {elasped:.1f}초, 출력 {msg.usage.output_tokens} 토큰")
    print(f"{text}")
