from dotenv import load_dotenv

# 프롬프트
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# 모델
from langchain_openai import ChatOpenAI
# 파서
from langchain_core.output_parsers import StrOutputParser
# 기타
from langchain_core.chat_history import InMemoryChatMessageHistory

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini") 

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 챗봇입니다."),
    MessagesPlaceholder("history"),
    ("user", "{input}"),
])

chain = prompt | llm | StrOutputParser()

history = InMemoryChatMessageHistory()

def chat(message):
    print(f"질문: {message}")
    answer = chain.invoke({
        "input": message,
        # "history": history.messages,    # 우리의 저장소에 있는 메시지 그대로 다
        "history": history.messages[-10:],    # 최근 10개의 대화만 가져온다
    })
    print(f"답변: {answer}")
    history.add_user_message(message)
    history.add_ai_message(answer)

chat("안녕하세요.")
chat("제 이름은 곽길동 입니다.")
chat("저는 겨울에 바닷가에 가서 서핑하는것을 좋아합니다.")
chat("제 이름과 취미가 뭐라고 했죠??")

questions = [
    "요즘 파이썬으로 챗봇을 만들고 있는데, 대화 히스토리를 어디까지 저장해야 할지 고민입니다.",
    "사용자가 이전에 말한 이름이나 취미는 기억하되, 너무 오래된 잡담은 줄이고 싶은데 좋은 방법이 있을까요?",
    "예를 들어 사용자가 여행 계획을 이야기했다면, 어떤 정보는 오래 기억하고 어떤 정보는 버려야 할까요?",
    "제가 이번 겨울에 강릉으로 서핑 여행을 가려고 하는데, 챙겨야 할 준비물을 정리해 주세요.",
    "겨울 바다에서 서핑할 때 안전하게 즐기려면 어떤 점을 특히 조심해야 하나요?",
]

for q in questions:
    chat(q)

chat("제 이름과 취미가 뭐라고 했죠??")
