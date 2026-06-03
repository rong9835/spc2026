import sqlite3

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent 

load_dotenv()

conn = sqlite3.connect(':memory:', check_same_thread=False)
conn.executescript(
    """
    CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, city TEXT, age INTEGER);
    CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price INTEGER, category TEXT);
    CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER, product_id INTEGER, qty INTEGER, ordered_at TEXT);

    INSERT INTO users (id, name, city, age) VALUES
        (1, "홍길동", "서울", 30), (2, "김철수", "부산", 25), 
        (3, "이영희", "서울", 28), (4, "박민수", "대구", 35);

    INSERT INTO products (id, name, price, category) VALUES
        (1, "노트북", 1500000, "전자"), (2, "마우스", 30000, "전자"), 
        (3, "책상", 200000, "가구"), (4, "의자", 150000, "가구");

    INSERT INTO orders(id, user_id, product_id, qty, ordered_at) VALUES
        (1, 1, 1, 1, '2026-05-01'), (2, 1, 2, 2, '2026-05-02'), 
        (3, 2, 3, 1, '2026-05-03'), (4, 3, 1, 1, '2026-05-04'), 
        (5, 3, 4, 4, '2026-05-05'), (6, 4, 2, 3, '2026-05-06');
    """
)
conn.commit()

SCHEMA = """
users(id, name, city, age)
products(id, name, price, category)  -- price 단위: 원
orders(id, user_id, product_id, qty, ordered_at) -- user_id=users.id, product_id=products.id
"""

@tool
def run_sql(query: str) -> str:
    """ SQLite DB 에 SQL 구문을 실행하고 결과를 반환한다. """
    q = query.strip().rstrip(";")
    cur = conn.execute(q)
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    if not rows:
        return "결과 없음"
    
    # 위에 쿼리 결과를 최대한 이쁘게 자연어로 반환하는 코드
    out = [" | ".join(cols)]
    out += [" | ".join(str(v) for v in row) for row in rows]
    return "\n".join(out)

SYSTEM = f""" 
당신은 SQLite 데이터 분석가입니다. 아래 스키마를 사용해서 질문에 응답하시오.

[스키마]
{SCHEMA}

규칙:
 - 답변을 할 때에는 run_sql 툴을 사용해서 쿼리문을 실행하시오.
 - SQLite3 문법만을 사용하고 JOIN, GROUP BY 등도 사용 가능 함.
"""

llm = ChatOpenAI(model="gpt-4o-mini")
agent = create_agent(llm, [run_sql], system_prompt=SYSTEM)

questions = [
    "서울사 사는 사용자는 몇 명이야?",
    "가장 비싼 상품 3개를 가격 높은 순으로 보여줘",
    "홍길동이 주문한 상품 이름과 수량을 보여줘",
    "카테고리별 총 주문 수량을 알려줘"
]

for q in questions:
    print(f"[질문]: {q}")
    result = agent.invoke({"messages": [("user", q)]})

    for m in result["messages"]:
        for call in getattr(m, "tool_calls", None) or []:
            print(f"  [실행한 쿼리] {call['args'].get('query')}")
    print(f"[답변] {result['messages'][-1].content}")
