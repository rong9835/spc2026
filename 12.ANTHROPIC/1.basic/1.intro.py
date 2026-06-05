# pip install anthropic
import os

# import openai
import anthropic

from dotenv import load_dotenv

load_dotenv()

# client = openai.OpenAI()
client = anthropic.Anthropic()

# message = client.chat.completion
message = client.messages.create(
    # haiku(빠름), sonnet, opus(최신, 고성능)
    model="claude-haiku-4-5",
    max_tokens=300,
    messages=[{
        "role":"user", "content": "안녕! 한 문장으로 너를 소개해줘."
    }]
)

print(message.content[0].text)
