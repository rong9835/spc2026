from flask import Flask

app = Flask(__name__)

@app.route('/user')
@app.route('/user/<username>')  # <변수>
def show_user_profile(username="익명"):
    return f"<H1>사용자: {username}</H1>"

@app.route('/admin')
def show_admin_profile():
    return "관리자: 홍길동"

@app.route('/product')
@app.route('/product/<int:id>')  # id를 숫자로 지정
def show_product(id=0):
    return f"상품코드: {id}, 상품명: 사과"


if __name__== '__main__':
    app.run(debug=True)

