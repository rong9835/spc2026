from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")
parser = StrOutputParser()

# ('[1단계] 리서치 수행중')
research_prompt = ChatPromptTemplate.from_template(
    "다음 주제에 대해 핵심 사실 5가지를 간결하게 정리해주세요"
    "\n\n주제: {topic}"
)
research_chain = research_prompt | llm | parser

# ('[2단계] 게이트 검증 수행중')
gate_prompt = ChatPromptTemplate.from_template(
"""
다음 리서치 결과가 적합한지 평가해 주세요.

---
리서치 결과: 
{research}

---
평가 기준:
1. 사실 5가지가 올바르게 포함되어 있는가?
2. 각 사실이 구체적이고 검증 가능한가?
3. 주제와 관련이 있는가?

---
결과:
PASS 또는 FAIL 로만 답하고, PASS인 경우 아무런 설명도 없이 PASS 만, 실패인 경우 이유를 한줄로 설명하시오.
"""
)

gate_chain = gate_prompt | llm | parser


# ('[3단계] 분석 수행중')
analysis_prompt = ChatPromptTemplate.from_template(
"""
다음 리서치 결과를 바탕으로 심층 분석 내용을 적상해주시오.

---
리서치 결과: 
{research}

---
다음을 포함해주세요:
- 핵심 트랜드 또는 패턴
- 시사점
- 향후 전장
"""
)

analysis_chain = gate_prompt | llm | parser


# ('[4단계] 보고서생성 수행중')
report_prompt = ChatPromptTemplate.from_template(
# (CEO에게 보고를 위한, 실무자가 팀장에게 보고하는 형태의, 등등 다양하게 바꿔볼것, 초등학생도 이해할수 있도록 쉬운 레벨로)
"""
다음 리서치와 분석 된 내용을 바탕으로 간결한 CEO에게 보고를 위한 보고서를 작성하시오.

---
리서치: 
{research}

---
분석: 
{analysis}

---
출력형식:
- 제목
- 요약 (3줄)
- 핵심 발견사항
- 결론
"""
# - 기본 디자인을 포함한 HTML 단일 파일 파일 문서로 CSS까지 포함
)

report_chain = report_prompt | llm | parser


def run_chaining_pipeline(topic):
    # 1단계: 리서치
    print('[1단계] 리서치 수행중')
    research = research_chain.invoke({'topic': topic})

    # 2단계: 게이트 검증
    print('[2단계] 게이트 검증 수행중')
    gate_result = gate_chain.invoke({'research': research})
    print("2단계 결과: ", gate_result)
    if gate_result.lower() in "fail":
        print("게인트 검증에 실패하여 해당 업무를 재수행 합니다.")
        gate_result = gate_chain.invoke({'research': research})
        # 고도화를 할거면, 반복 횟수 정의하거나, 프롬프트를 살짝씩 고도화 한거로 시키거나, 또는 모델(gpt-4o-mini) 대신 일 더 잘하는 애를 고용하거나 한다.

    # 3단계: 분석 수행
    print('[3단계] 분석 수행중')
    analysis = analysis_chain.invoke({'research': research})

    # 4단계: 보고서 생성
    print('[4단계] 보고서생성 수행중')
    report = report_chain.invoke({'research': research, 'analysis': analysis})

    return report


# 질문
# 1. 2026년도 생성형 AI 시장 동향 조사를 해오시오.
# topic = "2026년도 생성형 AI 시장 동향 조사를 해오시오."
topic = "2025년도의 한해동안의 주요 해킹 사례와 보안 기술 동향을 조사해줘"

result = run_chaining_pipeline(topic)
print('-' * 60)
print('최종 보고서:')
print('-' * 60)

# 리서치 -> 분석 -> 보고서
print(result)
