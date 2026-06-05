import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

model = 'claude-opus-4-8'

prompt = "12 x 13을 어떻게 푸는지 단계별로 설명해줘"

with client.messages.stream(
    model=model,
    max_tokens=2000,
    thinking={"type":"adaptive", "display": "summarized"},
    messages=[{"role":"user", "content": prompt}]
) as stream:
    for event in stream:
        if event.type == "content_block_start":
            if event.content_block.type == "thinking":
                print("\n[생각] ", end="", flush=True)
            elif event.content_block.type == "text":
                print("\n\n[답변] ", end="", flush=True)
        elif event.type == "content_block_delta":
            if event.delta.type == "thinking_delta":
                print(event.delta.thinking, end="", flush=True)
            elif event.delta.type == "text_delta":
                print(event.delta.text, end="", flush=True)
print()
