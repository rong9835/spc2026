from flask import Flask, request, jsonify, send_from_directory
import openai
import os
from dotenv import load_dotenv
import sqlite3

load_dotenv()

client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

app = Flask(
    __name__, static_folder='static', static_url_path=''
)  # static 폴더 경로와 그 prefix 를 결정(변경) 할 수 있음

# history = [] 이거를 대체할 DB 코드를 넣기
conn = sqlite3.connect('chatgpt.db', check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()


def init_db():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              session_id TEXT NOT NULL,
              user_id TEXT NOT NULL,
              role TEXT NOT NULL,
              content TEXT NOT NULL,
              timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()


init_db()


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    chat_message = data.get('chatMessage', '')
    session_id = data.get('sessionId', '')
    user_id = data.get('userId', '')
    print('사용자 입력값: ', chat_message)

    # 이거를 대체할 SQL INSERT 구문 넣기
    cursor.execute(
        'INSERT INTO history (session_id, user_id, role, content) VALUES (?, ?, ?, ?)',
        (session_id, user_id, 'user', chat_message),
    )
    conn.commit()

    # chatgpt 에게 물어보기...
    gpt_reply = ask_chatgpt(chat_message, session_id)

    # 이거를 대체할 SQL INSERT 구문 넣기
    cursor.execute(
        'INSERT INTO history (session_id, user_id, role, content) VALUES (?, ?, ?, ?)',
        (session_id, user_id, 'assistant', gpt_reply),
    )
    conn.commit()

    return jsonify({'reply': f'{gpt_reply}'})


def ask_chatgpt(chat_message, session_id):
    cursor.execute(
        'SELECT role, content FROM history WHERE session_id = ? ORDER BY id DESC LIMIT 10',
        (session_id,),
    )
    rows = cursor.fetchall()
    print('원본 쿼리문:', rows)
    rows = rows[::-1]  # 역순으로 다시 배열에 넣기
    print('역순 재변환:', rows)

    rows_dict = [{'role': row['role'], 'content': row['content']} for row in rows]
    print('-' * 30)
    print(rows_dict)

    gpt_ask_message = [
        {
            'role': 'system',
            'content': '당신은 친절한 챗봇입니다. 경상도 사투리를 적절하게 섞어서 답변하시오.',
        },
        *rows_dict,
    ]
    # 이거를 대체할 SQL SELECT 구문 넣기...

    print('>>>>>>>>>>')
    print('최종 GPT 에게 우리가 물어볼 전체 메시지: ', gpt_ask_message)
    print('<<<<<<<<<<')

    response = client.chat.completions.create(
        model='gpt-4o-mini',  # 왠만한 우리 실습은 gpt-4o-mini
        messages=gpt_ask_message,
    )
    print('출력확인:', response)
    return response.choices[0].message.content


@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    user_id = request.args.get('userId', '')
    cursor.execute('''
        SELECT session_id, content as title, timestamp
        FROM history
        WHERE user_id = ? AND role = 'user' AND id IN (
            SELECT MIN(id) FROM history WHERE user_id = ? AND role = 'user' GROUP BY session_id
        )
        ORDER BY timestamp DESC
    ''', (user_id, user_id))
    rows = cursor.fetchall()
    sessions = [{'sessionId': row['session_id'], 'title': row['title'][:30], 'timestamp': row['timestamp']} for row in rows]
    return jsonify({'sessions': sessions})


@app.route('/api/history', methods=['GET'])
def get_history():
    session_id = request.args.get('sessionId', '')
    cursor.execute(
        'SELECT role, content, timestamp FROM history WHERE session_id = ? ORDER BY id ASC',
        (session_id,)
    )
    rows = cursor.fetchall()
    history = [{'role': row['role'], 'content': row['content'], 'timestamp': row['timestamp']} for row in rows]
    return jsonify({'history': history})


@app.route('/api/history', methods=['DELETE'])
def delete_history():
    session_id = request.args.get('sessionId', '')
    cursor.execute('DELETE FROM history WHERE session_id = ?', (session_id,))
    conn.commit()
    return jsonify({'message': '대화 내역이 삭제되었습니다.'})


if __name__ == '__main__':
    app.run(debug=True)
