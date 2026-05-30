# pip install langchain-community
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

from langchain_community.chat_message_histories import SQLChatMessageHistory
from sqlalchemy import create_engine

load_dotenv()

DB_URL = "sqlite:///chat_history.db"
SESSION_ID = "default"   # 나중에 사용자별로 이걸 바꿔주면됨

engine = create_engine(DB_URL)
history = SQLChatMessageHistory(session_id=SESSION_ID, connection=engine)

llm = ChatOpenAI(model="gpt-4o-mini") 

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 챗봇입니다."),
    MessagesPlaceholder("history"),
    ("user", "{input}"),
])

chain = prompt | llm | StrOutputParser()


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

# chat("안녕하세요.")
# chat("제 이름은 곽길동 입니다.")
# chat("저는 겨울에 바닷가에 가서 서핑하는것을 좋아합니다.")
chat("제 이름과 취미가 뭐라고 했죠??")
