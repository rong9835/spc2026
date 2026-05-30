from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 한국어 어시스턴트 입니다."),
    MessagesPlaceholder("history"),
    ("user", "{input}")
])

chain = prompt | llm | StrOutputParser()

# 세션관리를 위한 자료구조
sessions: dict[str, InMemoryChatMessageHistory] = {}

# def get_session_history(session_id):
def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in sessions:
        sessions[session_id] = InMemoryChatMessageHistory()
    return sessions[session_id]

chain_with_memory = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

# def chat(message):
def chat(message, session_id):
    print(f"\n[{session_id}] 질문: {message}")
    answer = chain_with_memory.invoke(
        {"input":message},
        config={"configurable": {"session_id": session_id}},  # *** 여기가 세션 관리의 핵심 ***
    )
    print(f"[{session_id}] 답변: {answer}")

user_a = "user-A" # 세션ID 임의 생성
user_b = "user-B" # 세션ID 임의 생성

chat("제 이름은 홍길동 입니다.", user_a)
chat("제 이름은 김철수 입니다.", user_b)
chat("저는 등산을 좋아합니다.", user_a)
chat("저의 취미는 낚시 입니다.", user_b)
chat("저는 누구인가요??", user_a)
chat("저는 누구인가요??", user_b)
