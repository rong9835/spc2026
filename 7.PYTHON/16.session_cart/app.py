# Flask와 필요한 도구들을 가져옴
# session: 사용자별로 데이터를 기억하는 창고 (장바구니 저장에 사용)
# redirect: 다른 페이지로 강제 이동
# url_for: 함수 이름으로 주소를 자동 생성
from flask import Flask, render_template, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'hello1234'  # session 암호화에 필요한 비밀키 (없으면 session 사용 불가)

# 상품 목록 (실제 서비스에선 DB에서 가져오지만, 여기선 변수에 직접 저장)
items = [
    {'id': 'item1', 'name': '햄버거', 'price': 3000},
    {'id': 'item2', 'name': '핫도그', 'price': 2000},
    {'id': 'item3', 'name': '콜라', 'price': 1500},
]

# 홈(/) 접속 시 상품 목록 페이지를 보여줌
@app.route('/')
def index():
    return render_template('product.html', items=items)  # items 데이터를 HTML로 넘겨줌

# /add_to_cart/item1 처럼 접속하면 실행됨
# <item_id>: 주소에서 'item1', 'item2' 같은 값을 뽑아서 변수에 저장
@app.route('/add_to_cart/<item_id>')
def add_to_cart(item_id):
    print("장바구니에 담을 상품: ", item_id)

    # 세션에 장바구니가 없으면 (처음 사용하는 경우) 빈 딕셔너리로 만들어줌
    if 'cart' not in session:
        session['cart'] = {}

    if item_id in session['cart']:
        session['cart'][item_id] += 1  # 이미 담긴 상품이면 수량 +1
    else:
        # 장바구니에 담을 상품이 실제로 존재하는가??
        session['cart'][item_id] = 1   # 처음 담는 상품이면 수량 1로 설정

    print(session['cart'])
    session.modified = True  # 딕셔너리 내부를 직접 수정했을 때 Flask에게 변경됐다고 알려줌

    return redirect(url_for('index'))  # 장바구니 담기 후 홈으로 돌아감

# /cart 접속 시 장바구니 내용을 보여줌
@app.route('/cart')
def view_cart():
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
            'price': item['price']
        }
        total_price += item['price'] * quantity  # 총 금액 누적 (단가 × 수량)

    return render_template('cart.html', cart_items=cart_items, total_price=total_price)  # 장바구니 HTML로 데이터 넘겨줌

# 이 파일을 직접 실행할 때만 서버 시작 (다른 파일에서 import하면 실행 안 됨)
if __name__ == '__main__':
    app.run(debug=True)  # debug=True: 코드 수정 시 자동 재시작, 에러 상세 표시
