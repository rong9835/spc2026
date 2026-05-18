from flask import Flask, make_response, request

app = Flask(__name__)


@app.route("/")
def main():
    cookie = request.cookies.get("my-data")
    # 쿠키가 있으면
    if cookie:
        return f"안녕, {cookie}야"

    # 쿠키가 없으면

    resp = make_response("안녕하세요, 첫 방문이시군요")
    resp.set_cookie("my_data,", "spc2026")
    return resp


if __name__ == "__main__":
    app.run(debug=True)
