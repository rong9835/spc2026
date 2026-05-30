import json
from wcwidth import wcswidth

def ljust_display(text, width):
    text = str(text)
    padding = width - wcswidth(text)
    return text + " " * max(0, padding)

with open("history.json", "r", encoding="utf-8") as f:
    messages = json.load(f)

ROLE = {"human": "사용자", "ai": "챗봇", "system": "시스템"}

print(f"=== {len(messages)} 메시지 ===")

for i, m in enumerate(messages, 1):
    role = ROLE.get(m.get("type"), "기타")
    content = m.get("data", {}).get("content", "")
    print(f"{i:02d}. [{ljust_display(role, 8)}] {content}")
