from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate


load_dotenv()

llm = ChatAnthropic(model='claude-sonnet-4-6')

template = PromptTemplate.from_template('다음 주제에 대해 설명하시오{topic}')


# formatted_prompt = template.format(topic='LLM기술')
# response = llm.invoke(formatted_prompt)
# print(response.content)


# formatted_prompt = template.format(topic='transformer 기술')
# response = llm.invoke(formatted_prompt)
# print(response.content)


###################
chat_template = ChatPromptTemplate.from_messages(
    [
        ('system', '당신은 {role} 전문가입니다. 질문에 자세히 답변해주세요.'),
        ('human', '다음 개념에 대해서 설명해주세요 : {concept}'),
    ]
)


chain = chat_template | llm
result = chain.invoke({'role': '인공지능', 'concept': '트랜스포머'})
print(result.content)
