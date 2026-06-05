import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

# 대화 내용을 저장할 배열을 만듦
messages = []

def ask(question):
    print("[질문] ", question)

    messages.append({'role':'user', 'content': question})

    message = client.messages.create(
        # haiku(빠름), sonnet, opus(최신, 고성능 = thinkikng)
        model="claude-haiku-4-5",
        max_tokens=300,
        temperature=1.0,
        messages=messages
    )

    answer = message.content[0].text
    messages.append({'role':'assistant', 'content': answer})
    return answer

print("[챗봇] ", ask("내 이름은 홍길동이야"))
print("[챗봇] ", ask("그래서, 내가 누구라고??"))
