# 🛍️ AI 쇼핑몰 리뷰 프로젝트 핵심 요약

## 프로젝트가 하는 일

> 사용자가 상품 리뷰(별점 + 후기)를 남기면,  
> AI가 모든 리뷰를 자동으로 요약해서 보여주는 쇼핑몰 페이지

---

## 📁 파일 구조

```
3.shopping/
├── app.py            # 서버 (Python/Flask) - 뒤에서 데이터를 처리
└── public/
    └── index.html    # 화면 (HTML/JS) - 사용자가 보는 페이지
```

---

## 🏗️ 전체 동작 흐름

```
[사용자] → 별점 + 후기 입력 → [제출 버튼 클릭]
                                      ↓
                           [JS] fetch POST /api/reviews
                                      ↓
                           [Flask] reviews 리스트에 저장
                                      ↓
                           [JS] loadReviews() 다시 호출
                                      ↓
                  ┌────────────────────────────────────┐
                  │  fetch GET /api/reviews (리뷰 목록)  │
                  │  fetch GET /api/ai-summary (AI 요약) │
                  └────────────────────────────────────┘
                                      ↓
                           [화면에 표시]
```

---

## 🐍 app.py 핵심 정리

### 1. 기본 세팅

```python
reviews = []  # 리뷰를 메모리에 저장하는 리스트
              # ⚠️ 서버 재시작하면 데이터 사라짐 (실제 서비스엔 DB 사용)
```

### 2. 리뷰 저장 API

```python
@app.route('/api/reviews', methods=['POST'])
def add_review():
    data = request.get_json()       # 프론트에서 보낸 JSON 받기
    reviews.append({
        'rating': data['rating'],   # 별점 (1~5)
        'comment': data['comment']  # 후기 텍스트
    })
    return jsonify({'message': '저장완료'})
```

| 항목 | 내용 |
|------|------|
| 주소 | `/api/reviews` |
| 방식 | POST |
| 받는 데이터 | `{"rating": "5", "comment": "좋아요"}` |
| 돌려주는 것 | `{"message": "저장완료"}` |

### 3. 리뷰 조회 API

```python
@app.route('/api/reviews', methods=['GET'])
def get_review():
    return jsonify({'data': reviews})
```

| 항목 | 내용 |
|------|------|
| 주소 | `/api/reviews` |
| 방식 | GET |
| 돌려주는 것 | `{"data": [{"rating":"5","comment":"좋아요"}, ...]}` |

> 💡 **같은 주소, 다른 역할** - `/api/reviews`는 POST면 저장, GET이면 조회  
> HTTP 메서드로 역할을 구분하는 것이 REST API 방식!

### 4. AI 요약 API

```python
@app.route('/api/ai-summary')
def get_ai_summary():
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {'role': 'system', 'content': '너는 쇼핑몰 리뷰를 요약해주는 AI야'},
            {'role': 'user',   'content': str(reviews)},  # 모든 리뷰를 문자열로 전달
        ]
    )
    return jsonify({'message': response.choices[0].message.content})
```

| 항목 | 내용 |
|------|------|
| 주소 | `/api/ai-summary` |
| 방식 | GET |
| 하는 일 | 모든 리뷰를 GPT에게 전달 → AI가 요약 → 결과 반환 |

---

## 🌐 index.html 핵심 정리

### 1. 페이지 로드 시 리뷰 불러오기

```javascript
async function loadReviews() {
    // ① 리뷰 목록 가져오기
    const reviewsResponse = await fetch('/api/reviews');
    const reviewData = await reviewsResponse.json();
    const reviews = reviewData.data;

    // ② 평균 별점 계산
    let total = 0;
    for (let i = 0; i < reviews.length; i++) {
        total = total + Number(reviews[i].rating);
    }
    const avg = (total / reviews.length).toFixed(1);  // 소수점 1자리

    // ③ AI 요약 가져오기 (리뷰가 있을 때만)
    if (reviews.length > 0) {
        const aiResponse = await fetch('/api/ai-summary');
        const aiData = await aiResponse.json();
        aiSummary = aiData.message;
    }

    // ④ 화면에 표시
    document.getElementById('review-container').innerHTML = `...`;
}
loadReviews();  // 페이지 열자마자 실행
```

### 2. 리뷰 제출

```javascript
document.getElementById('send').addEventListener('click', async () => {
    await fetch('/api/reviews', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            rating: document.querySelector('input[name="rating"]:checked').value,
            comment: document.getElementById('comment').value,
        }),
    });
    loadReviews();  // 제출 후 화면 새로고침
});
```

---

## 🔑 핵심 개념 3가지

### 1. REST API
같은 주소라도 **HTTP 메서드**로 다른 동작을 수행

| 메서드 | 역할 | 비유 |
|--------|------|------|
| GET | 데이터 조회 | 서랍에서 꺼내기 |
| POST | 데이터 저장 | 서랍에 넣기 |

### 2. fetch (비동기 통신)
```javascript
// 화면을 멈추지 않고 서버와 통신
const response = await fetch('/api/reviews');
const data = await response.json();  // JSON → 자바스크립트 객체로 변환
```
> `await` = "서버 응답 올 때까지 기다려줘"

### 3. OpenAI API 호출 구조
```python
client.chat.completions.create(
    model='gpt-4o-mini',     # 사용할 AI 모델
    messages=[
        {'role': 'system', 'content': 'AI의 역할 지정'},   # 시스템 프롬프트
        {'role': 'user',   'content': '실제 요청 내용'},   # 사용자 입력
    ]
)
```

---

## ⚠️ 이 프로젝트의 한계 (실제 서비스라면 개선 필요)

| 문제 | 이유 | 해결 방법 |
|------|------|-----------|
| 서버 재시작 시 리뷰 사라짐 | `reviews = []`는 메모리 저장 | DB 사용 (SQLite, PostgreSQL 등) |
| 리뷰 많으면 AI 요약 느림 | 매 요청마다 GPT 호출 | 결과 캐시 저장 |
| 아무나 리뷰 작성 가능 | 로그인 기능 없음 | 회원가입/로그인 추가 |

---

## 🚀 실행 방법

```bash
# 1. 환경 변수 설정 (.env 파일)
OPENAI_API_KEY=sk-...

# 2. 서버 실행
python app.py

# 3. 브라우저에서 접속
http://localhost:5000
```
