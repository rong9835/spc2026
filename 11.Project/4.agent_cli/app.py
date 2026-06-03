# 금융 도우미 에이전트 챗봇 만들기

# 랭체인들을 불러온다

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage
from flask import Flask, render_template, request, jsonify

load_dotenv()


from fin_tools import TOOLS

app = Flask(__name__)

SYSTEM = """
당신은 금융 정보 비서입니다.주가, 환율, 뉴스를 조회해서 답변해주세요.
"""
llm = ChatOpenAI(model='gpt-4o-mini')
agent = create_agent(llm, TOOLS)


def ask(q):
    result = agent.invoke({'messages': [('user', q)]})
    print('[질문]', q)
    return result['messages'][-1].content


# if __name__ == '__main__':
#     print('=== 데모 명령어 실행 ===')
#     for q in [
#         '삼성전자 주가 알려줘',
#         '달러 환율 얼마야?',
#         '엔비디아 관련 최근 뉴스는 뭐가 있어?',
#     ]:
#         ask(q)
#         print(ask(q))

#     print('=== 수동 질의 응답 시작 ===')
#     while True:
#         # 사용자로부터 질문을 받아서 'q', 'quit', 'exit', 가 올때까지 반복한다.
#         q = input('질문:').strip()


#         if not q or q.lower() in ('q', 'quit', 'exit'):
#             break
#         print(ask(q))
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ask', methods=['POST'])
def ask_route():
    q = request.json['question']
    answer = ask(q)
    return jsonify({'answer': answer})


if __name__ == '__main__':
    app.run(debug=True)
