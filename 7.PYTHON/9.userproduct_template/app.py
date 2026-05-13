from flask import Flask, render_template, request

# 1. /user 라는 경로를 만들고 URL파라미터를 기반으로 사용자를 조회할수 있게 한다.
#    /user는 모든 사용자 /user/1 홍길동 /user/2 김철수 등
# 2. /product 로 쿼리 파라미터를 기반으로 상품을 조회할수 있다
#    /product는 모든 상품, /product?id=101 로 상품 검색 ?name 으로도 상품 검색

app = Flask(__name__)

# dict 에 dict 는 인덱싱을 통한 빠른 조회 가능 (굳이 for u in users 이런거 안해도 됨)
users = {
    1: {"id": 1, "name": "홍길동", "email": "hong@example.com"},
    2: {"id": 2, "name": "김철수", "email": "kim@example.com"},
    3: {"id": 3, "name": "이영희", "email": "lee@example.com"},
    4: {"id": 4, "name": "박민수", "email": "park@example.com"},
    5: {"id": 5, "name": "최지우", "email": "choi@example.com"},
}

products = {
    101: {"id": 101, "name": "Laptop", "price": 1200},
    102: {"id": 102, "name": "Keyboard", "price": 80},
    103: {"id": 103, "name": "Mouse", "price": 40},
    104: {"id": 104, "name": "Monitor", "price": 300},
    105: {"id": 105, "name": "Headset", "price": 150},
    106: {"id": 106, "name": "Laptop", "price": 1500},
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/user')
@app.route('/user/<int:user_id>')
def user(user_id=None):
    return render_template("user.html", user_id=user_id, users=users)

@app.route('/product')
def product():
    id = request.args.get('id', type=int)
    name = request.args.get("name", type=str)

    found = list(products.values())
    if id:
        found = [p    for p in found    if p["id"] == id]
    if name:
        found = [p    for p in found    if p["name"].lower() == name.lower()]

    return render_template("product.html", results=found)

if __name__ == "__main__":
    app.run(debug=True)
