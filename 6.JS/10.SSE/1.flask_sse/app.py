# 별도의 라이브러리 없이.. 그냥 Flask에 있는 Response 라는걸 통해서.. stream event를 줄수 있다.

from flask import Flask, send_from_directory
from flask import request, Response
from queue import Queue

app = Flask(__name__)

# 연결된 사용자들 관리
clients = []

@app.route('/')
def index():
    return send_from_directory("static", "index.html")

# 클라이언트에세 응답을 보낼 API - SSE 방식으로 보낼 API, 상대방이 여기를 바라보고 있으면, 내가 여기를 통해서 메시지를 보낼때마다, 클라에게 전달됨 => 이걸 event-stream 이라고 함
@app.route("/stream")
def stream():
    print("클라이언트 연결됨 - 누가 이 API를 듣고 있음")

    def event_stream():
        q = Queue()
        clients.append(q) # 응답을 보낼 사용자 목록에 이 새로온 사용자를 추가
        try:
            yield f"data: 서버에 연결되었습니다!\n\n" # 웹표준 event-stream으로 보낼때 data: <메시지>\n\n"

            while True:
                message = q.get()
                if message is None:
                    break
                yield f"data: {message}\n\n"
        except GeneratorExit:
            print("클라 연결 종료")
        finally:
            clients.remove(q)

    return Response(event_stream(), mimetype="text/event-stream")

# 클라이언트가 나에게 보내는 API
@app.route("/send", methods=["POST"])
def send():
    message = request.form.get("msg", "")
    print("클라이언트 메시지: ", message)
    for q in clients:
        q.put(f"서버가 받은 메시지: {message}")
    return ("", 204)

if __name__ == "__main__":
    app.run(debug=True)
