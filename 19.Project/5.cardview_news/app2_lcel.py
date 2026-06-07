# pip install lxml

import base64, requests
from bs4 import BeautifulSoup

from dotenv import load_dotenv

from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")
client = OpenAI()


def fetch_news(query):
    """뉴스 검색 결과를 가져온다."""
    url = "https://news.google.com/rss/search"
    params = {
        "q": query,
        "hl": "ko",
        "gl": "KR",
        "ceid": "KR:ko"
    }

    xml = requests.get(url, params=params, timeout=10).text
    soup = BeautifulSoup(xml, "xml")

    items = []
    for item in soup.find_all("items")[:8]:
        items.append({
            "title": item.title.text,
            "link": item.link.text,
            "date": item.pubDate.text
        })
    return str(items)

def make_image_prompt(news):
    prompt = f"""
다음 뉴스 내용을 바탕으로 웹툰형 카드뉴스 이미지 생성 프롬프르를 만드시오.

조건:
- 한 장짜리 이미지
- 여러 컷 웹툰 스타일
- 한국어 텍스트 포함
- 날짜가 있다면, 각 날짜별로 패널을 구성
- 뉴스 카드 + 만화 컷 + 인포그래픽 형태로 혼합 구성
- 인물은 실제 해당 유명인을 캐릭터화 한 느낌으로 생성
- 회사 로고나 상표 등을 적절하게 활용해서 실제 내용을 살림

뉴스:
{news}
    """

    result = llm.invoke(prompt)
    return result.content

def generate_image(image_prompt, output="output.png"):
    result = client.images.generate(
        model="gpt-image-1.5",
        prompt=image_prompt,
        size="1024x1536",
        quality="medium"
    )

    image_base64 = result.data[0].b64_json
    with open(output, "wb") as f:
        f.write(base64.b64decode(image_base64))

    return output

news_agent = create_agent(
    model=llm,
    tools=[fetch_news],
    system_prompt="""
너는 뉴스 조사 에이전트다.
사용자 주제와 관련된 뉴스 목록을 수집하고, 일정/날짜/행사/만남 정보를 중심으로 정리한다.
"""
)

summarize_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "너는 OOO 이다..."),
        ("human", "다음 뉴스로 OOo 해라.")
    ])
    | llm
    | StrOutputParser()
)

pipeline = (
    RunnablePassthrough.assign(news=fetch_news)
    | RunnablePassthrough.assign(summary=summarize_chain)
    | RunnablePassthrough.assign(image_prompt=image_prompt)
    | RunnablePassthrough.assign(image_path=generate_image)
)

def main():
    result = pipeline.invoke({"query": "젠슨 황 4박 5일 한국 방문 일정 뉴스들을 조사해줘"})
    print("\n[뉴스 요약]")
    print(result['summary'])
    print('-' * 60)

    # 2. 뉴스 요약 및 이미지 생성 프롬프트
    image_prompt = make_image_prompt(news)
    print("\n[이미지 프롬프트]")
    print(image_prompt)

    # 3. 이미지 생성
    output_file = generate_image(image_prompt)
    print(f"\n이미지 생성 완료: {output_file}")

if __name__ == "__main__":
    main()
