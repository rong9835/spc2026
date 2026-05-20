from flask import Flask, render_template, session, redirect, url_for, request


items = [
    {'id': 'item1', 'name': '햄버거', 'price': 3000},
    {'id': 'item2', 'name': '핫도그', 'price': 2000},
    {'id': 'item3', 'name': '콜라', 'price': 1500},
]
users = [
    {'name': 'Alice', 'id': 'alice', 'pw': 'alice'},
    {'name': 'Bob', 'id': 'bob', 'pw': 'bob1234'},
    {'name': 'Charlie', 'id': 'charlie', 'pw': 'hello'},
]

app = Flask(__name__)
app.secret_key = 'hello1234'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    # 1. 요청에서 id/pw 가져온다
    id = request.form.get('id')
    pw = request.form.get('pw')

    # 2. user db에서 이 사용자 매칭한다
    user = next((u for u in users if u['id'] == id and u['pw'] == pw), None)

    # 3. 사용자가 있으면??
    if user:
        session['user'] = user  # 로그인한 사용자를 세션에 저장한다.
        return redirect(url_for('welcome'))

    return render_template('login.html', error='아이디 또는 비밀번호가 틀렸습니다')


@app.route('/')
def welcome():
    if not session.get('user'):
        return redirect(url_for('login'))
    return render_template('home.html', user=session['user'])


@app.route('/cart')
def cart():
    cart_items = {}  # HTML에 넘겨줄 장바구니 정보를 담을 딕셔너리
    total_price = 0  # 총 금액 초기값

    # 세션 장바구니를 꺼내서 하나씩 순회 (장바구니가 없으면 빈 딕셔너리로 에러 방지)
    for item_id, quantity in session.get('cart', {}).items():
        # 상품 목록에서 item_id가 일치하는 상품을 찾음 (없으면 None)
        item = next((i for i in items if i['id'] == item_id), None)
        # 화면에 보여줄 상품 정보 정리
        cart_items[item_id] = {
            'name': item['name'],
            'quantity': quantity,
            'price': item['price'],
        }
        total_price += item['price'] * quantity  # 총 금액 누적 (단가 × 수량)

    return render_template(
        'cart.html', cart_items=cart_items, total_price=total_price
    )  # 장바구니 HTML로 데이터 넘겨줌


@app.route('/list')
def list():
    return render_template('list.html', items=items)


@app.route('/product_list/<item_id>')
def product_list(item_id):
    # 로그인 안 했으면 로그인 페이지로!
    if not session.get('user'):
        return redirect(url_for('login'))

    # 세션에 장바구니가 없으면 (처음 사용하는 경우) 빈 딕셔너리로 만들어줌
    if 'cart' not in session:
        session['cart'] = {}

    if item_id in session['cart']:
        session['cart'][item_id] += 1  # 이미 담긴 상품이면 수량 +1
    else:
        # 장바구니에 담을 상품이 실제로 존재하는가??
        session['cart'][item_id] = 1  # 처음 담는 상품이면 수량 1로 설정

    print(session['cart'])
    session.modified = (
        True  # 딕셔너리 내부를 직접 수정했을 때 Flask에게 변경됐다고 알려줌
    )

    return redirect(url_for('list'))  # 장바구니 담기 후 상품목록으로 돌아감


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/remove/<item_id>')
def remove(item_id):
    if 'cart' in session and item_id in session['cart']:
        del session['cart'][item_id]
        session.modified = True
    return redirect(url_for('cart'))


if __name__ == '__main__':
    app.run(debug=True)
