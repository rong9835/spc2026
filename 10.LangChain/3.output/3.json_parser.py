from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")

parser = JsonOutputParser()

prompt = ChatPromptTemplate.from_messages([
    ("system", "답변은 항상 JSON으로만 하시오. 설명 금지"),
    ("user", "{question}\n\n{format_instruction}")
]).partial(format_instruction=parser.get_format_instructions())  # 고정값을 미리 채워준다

chain = prompt | llm | parser

result = chain.invoke({"question": "아시아에서 인구가 가장 많은 나라 3개의 이름과 수도를 알려줘"})
print(f"결과: {result}")
