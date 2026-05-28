from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from pydantic import BaseModel, Field

load_dotenv()

class MovieReview(BaseModel):
    """ 영화 리뷰 분석 결과 """
    title: str = Field(description="영화 제목")
    sentiment: str = Field(description="감성 분류: 긍정, 부정, 중립")
    score: int = Field(description="1~10 점수")
    summary: str = Field(description="리뷰 요약 (1~2문장)")
    keywords: list[str] = Field(description="핵심 키워드 3개")

llm = ChatOpenAI(model="gpt-4o-mini")

parser = PydanticOutputParser(pydantic_object=MovieReview)
# print("포멧 명령문:")
# print(parser.get_format_instructions())

prompt = ChatPromptTemplate.from_template(
    """ 다음 영화 리뷰를 분석해 주세요.
리뷰: {review}

{format_instructions}
"""
)

chain = prompt | llm | parser

reviews = [
    "영화 《Project Hail Mary》는 우주 생존물 특유의 긴장감과 감동을 동시에 잘 살린 작품이었다. 특히 주인공의 외로움과 유머가 절묘하게 섞여 몰입감이 상당했다. SF 좋아하는 사람이라면 꼭 볼 만하다.",
    "《The Mandalorian and Grogu》는 기존 스타워즈 팬들에게는 반가운 분위기를 제대로 살린 영화였다. 액션은 안정적이었지만 스토리는 다소 안전하게 흘러가서 신선함은 조금 부족했다. 그래도 그로구의 존재감 하나만으로 볼 가치가 충분했다.",
    "공포영화 《Obsession》은 저예산 영화라는 게 믿기지 않을 정도로 분위기 연출이 뛰어났다. 단순한 점프 스케어보다 심리적으로 조여오는 공포가 인상적이었다. 올해 가장 의외의 수작이라는 평가가 괜히 나온 게 아니다."
]

for review in reviews:
    result = chain.invoke({
        "review": review,
        "format_instructions": parser.get_format_instructions()
    })

    print(f"제목: {result.title}")
    print(f"감성: {result.sentiment} (점수: {result.score}/10)")
    print(f"요약: {result.summary}")
    print(f"키워드: {result.keywords}")
    print('-' * 30)
