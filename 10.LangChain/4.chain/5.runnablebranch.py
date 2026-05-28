from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")

def make_chain(role):
    return (
        ChatPromptTemplate.from_messages([
            ("system", role),
            ("user", "{question}")
        ])
        | llm
        | StrOutputParser()
    )

# 개발자냐/요리사냐/일반
code_chain = make_chain("당신은 파이썬 개발자입니다.")
cook_chain = make_chain("당신은 요리 전문가입니다.")
general_chain = make_chain("당신은 일반 어시스턴트 입니다.")

branch = RunnableBranch(
    (
        lambda x: "파이썬" in x["question"] or "코드" in x["question"],
        code_chain
    ),
    (
        lambda x: "요리" in x["question"] or "레시피" in x["question"],
        cook_chain
    ),
    general_chain
)

questions = [
    "파이썬 리스트 정렬 코드 알려줘",
    "김치찌개 레시피 알려줘",
    "오늘 날씨 어때?"
]

for q in questions:
    print("질문:", q)
    print("답변:", branch.invoke({"question": q}))
    print('-' * 60)
