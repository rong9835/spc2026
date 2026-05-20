#  1단계 → DB 테이블 만들기 (database.py에 테이블 생성 코드 추가)
#   2단계 → /create API 완성 (메모 저장)
#   3단계 → /list API 완성 (메모 목록 가져오기)
#   4단계 → script.js 작성 (저장 버튼 클릭하면 서버에 전송)
#   5단계 → 화면에 목록 표시
#   6단계 → 삭제/수정


from flask import Flask, send_from_directory, jsonify, request
from database import MyDatabase

app = Flask(__name__)
db = MyDatabase()


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/create', methods=['POST'])
def create():
    title = request.json.get('title')
    message = request.json.get('message')
    sql = 'INSERT INTO board (title,message) VALUES (?,?)'

    db.execute(sql, (title, message))
    db.commit()

    return jsonify({'result': 'success'})


@app.route('/list')
def list():
    sql = 'SELECT * FROM board '
    result = db.execute_fetch(sql)
    return jsonify({'result': result})


@app.route('/delete', methods=['POST'])
def delete():
    return jsonify({'result': 'success'})


@app.route('/modify', methods=['POST'])
def modify():
    return jsonify({'result': 'success'})


if __name__ == '__main__':
    app.run(debug=True)
