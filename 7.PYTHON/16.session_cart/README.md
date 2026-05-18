# 세션(Session)으로 장바구니 만들기

## 핵심 개념 — 세션이란?

> **세션 = 서버가 사용자를 기억하는 메모장**

웹 서버는 원래 사용자를 기억 못 합니다.  
페이지를 이동하면 "처음 만난 사람" 취급해요.

그래서 **세션**을 사용합니다.

```
사용자 ──로그인──▶ 서버가 메모장(세션) 생성
사용자 ──이동──▶ 서버가 메모장 꺼내서 확인
사용자 ──로그아웃──▶ 메모장 삭제
```

쿠키 vs 세션 차이:

| 구분 | 쿠키 | 세션 |
|------|------|------|
| 저장 위치 | 사용자 브라우저 | 서버 |
| 보안 | 낮음 (사용자가 볼 수 있음) | 높음 (서버에만 있음) |
| 용도 | 작은 설정값 | 로그인 상태, 장바구니 |

---

## 프로젝트 구조

```
16.session_cart/
├── app.py                  ← Flask 서버 (핵심 로직)
└── templates/
    ├── product.html        ← 상품 목록 페이지
    └── cart.html           ← 장바구니 페이지
```

---

## 전체 흐름 한눈에 보기

```
[상품 목록 페이지]
    → 사용자가 "카트에 추가" 클릭
    → /add_to_cart/item1 요청
    → 세션에 { item1: 1 } 저장
    → 다시 상품 목록으로 이동

[장바구니 페이지]
    → 세션에서 cart 꺼내기
    → 상품 정보 + 수량 + 가격 계산
    → 화면에 출력
```

---

## app.py 핵심 코드 분석

### 1. 세션 사용을 위한 준비

```python
from flask import Flask, session

app = Flask(__name__)
app.secret_key = 'hello1234'   # ← 세션 암호화 키 (필수!)
```

> `secret_key`는 세션 데이터를 **암호화**하는 열쇠예요.  
> 없으면 세션을 쓸 수 없어요. 실제 서비스에서는 절대 코드에 하드코딩하지 않아요.

---

### 2. 상품 데이터 (DB 대신 리스트로 흉내)

```python
items = [
    {'id': 'item1', 'name': '햄버거', 'price': 3000},
    {'id': 'item2', 'name': '핫도그', 'price': 2000},
    {'id': 'item3', 'name': '콜라',   'price': 1500},
]
```

---

### 3. 장바구니에 담기 (`/add_to_cart/<item_id>`)

```python
@app.route('/add_to_cart/<item_id>')
def add_to_cart(item_id):

    # 세션에 cart가 없으면 빈 딕셔너리로 시작
    if 'cart' not in session:
        session['cart'] = {}

    # 이미 담긴 상품이면 수량 +1, 없으면 1로 시작
    if item_id in session['cart']:
        session['cart'][item_id] += 1
    else:
        session['cart'][item_id] = 1

    session.modified = True   # ← 세션이 바뀌었다고 Flask에게 알려줌
    return redirect(url_for('index'))
```

**세션 안의 cart 생김새:**
```python
# 햄버거 2개, 콜라 1개 담았을 때
session['cart'] = {
    'item1': 2,   # 햄버거
    'item3': 1,   # 콜라
}
```

> **왜 `session.modified = True`가 필요할까?**  
> 딕셔너리 내부 값을 바꿨을 때, Flask가 변경을 감지 못 할 수 있어요.  
> 이 한 줄로 "나 바뀌었어!" 라고 명시적으로 알려줍니다.

---

### 4. 장바구니 보기 (`/cart`)

```python
@app.route('/cart')
def view_cart():
    cart_items = {}
    total_price = 0

    # 세션의 cart를 꺼내서 반복
    for item_id, quantity in session.get('cart', {}).items():

        # item_id로 실제 상품 정보 찾기
        item = next((i for i in items if i['id'] == item_id), None)

        cart_items[item_id] = {
            'name': item['name'],
            'quantity': quantity,
            'price': item['price']
        }
        total_price += item['price'] * quantity   # 가격 합산

    return render_template('cart.html', cart_items=cart_items, total_price=total_price)
```

**cart_items 생김새 (템플릿에 전달되는 데이터):**
```python
{
    'item1': {'name': '햄버거', 'quantity': 2, 'price': 3000},
    'item3': {'name': '콜라',   'quantity': 1, 'price': 1500},
}
# total_price = 3000*2 + 1500*1 = 7500
```

---

## 템플릿 핵심 코드

### product.html — 상품 목록

```html
{% for item in items %}
<li>
    {{ item.name }} (가격: {{ item.price }}원)
    <a href="{{ url_for('add_to_cart', item_id=item.id) }}">카트에 추가</a>
</li>
{% endfor %}
```

> `url_for('add_to_cart', item_id=item.id)`  
> → `/add_to_cart/item1` 같은 URL을 자동으로 만들어줘요.

---

### cart.html — 장바구니

```html
{% for item_id, item_info in cart_items.items() %}
<tr>
    <td>{{ item_info.name }}</td>
    <td>{{ item_info.quantity }}</td>
    <td>{{ item_info.price * item_info.quantity }}원</td>
</tr>
{% endfor %}

<p>전체 가격: {{ total_price }}원</p>
```

> 딕셔너리를 반복할 때는 `.items()`로 **키, 값을 동시에** 꺼내요.

---

## URL 라우팅 요약

| URL | 함수 | 하는 일 |
|-----|------|---------|
| `/` | `index()` | 상품 목록 보여주기 |
| `/add_to_cart/<item_id>` | `add_to_cart()` | 세션 cart에 상품 추가 |
| `/cart` | `view_cart()` | 장바구니 내용 보여주기 |

---

## 핵심 포인트 정리

```
✅ session['키'] = 값          → 세션에 저장
✅ session.get('키', 기본값)   → 세션에서 꺼내기 (없으면 기본값)
✅ session.modified = True     → 딕셔너리 내부 변경 후 필수!
✅ app.secret_key              → 세션 사용을 위해 반드시 설정
```
