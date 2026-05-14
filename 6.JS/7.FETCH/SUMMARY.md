# JavaScript Fetch API 핵심요약

## 1. Fetch란?

브라우저가 **외부 서버에 HTTP 요청**을 보내고 응답을 받아오는 내장 함수.
페이지를 새로고침하지 않고 데이터를 주고받는다 (비동기).

---

## 2. Fetch 기본 흐름

```
요청 → 응답(Response 객체) → JSON 파싱 → 데이터 사용
```

```javascript
fetch('URL')
  .then((response) => {        // 1단계: 응답 도착
    if (!response.ok) {
      throw new Error('오류 발생');
    }
    return response.json();    // 2단계: JSON으로 파싱 요청
  })
  .then((data) => {            // 3단계: 파싱된 데이터 사용
    console.log(data);
  })
  .catch((error) => {          // 에러 처리
    console.log(error);
  });
```

> **핵심**: `fetch()`는 응답 자체(Response 객체)를 먼저 주고, `.json()`을 호출해야 실제 데이터를 꺼낼 수 있다.

---

## 3. HTTP 메서드 (CRUD)

| 메서드 | 의미 | 용도 |
|--------|------|------|
| `GET` | 읽기 | 데이터 조회 (기본값) |
| `POST` | 생성 | 새 데이터 추가 |
| `PUT` | 수정 | 기존 데이터 전체 교체 |
| `DELETE` | 삭제 | 데이터 삭제 |

### GET (기본, 옵션 생략 가능)
```javascript
fetch('https://jsonplaceholder.typicode.com/users/1')
  .then(resp => resp.json())
  .then(data => console.log(data));
```

### POST (데이터 생성)
```javascript
fetch('https://jsonplaceholder.typicode.com/posts', {
  method: 'POST',
  headers: {
    'Content-type': 'application/json; charset=UTF-8'
  },
  body: JSON.stringify({ title: 'hello', body: 'world', userId: 1 })
})
  .then(resp => resp.json())
  .then(data => console.log(data));
```

### PUT (데이터 수정)
```javascript
fetch('https://jsonplaceholder.typicode.com/posts/1', {
  method: 'PUT',
  headers: { 'Content-type': 'application/json; charset=UTF-8' },
  body: JSON.stringify({ title: 'hello', body: 'world', userId: 1, id: 1 })
})
  .then(resp => resp.json())
  .then(data => console.log(data));
```

### DELETE (데이터 삭제)
```javascript
fetch('https://jsonplaceholder.typicode.com/posts/1', {
  method: 'DELETE'
});
```

---

## 4. 응답 데이터를 DOM에 렌더링

```javascript
fetch('https://jsonplaceholder.typicode.com/todos/1')
  .then(resp => resp.json())
  .then(data => {
    document.getElementById('result').innerHTML = `
      <ul>
        <li>Id: ${data.id}</li>
        <li>Title: ${data.title}</li>
      </ul>
    `;
  });
```

> 받아온 데이터를 **템플릿 리터럴(백틱)** 로 HTML에 끼워 넣는다.

---

## 5. URL에 변수 넣기 (동적 요청)

```javascript
const userid = document.getElementById('uid').value;

fetch(`https://jsonplaceholder.typicode.com/users/${userid}`)
  .then(resp => resp.json())
  .then(data => console.log(data));
```

> 입력값을 URL에 넣어 원하는 ID의 데이터만 요청할 수 있다.

---

## 6. 실습 예제 정리

### 랜덤 강아지 이미지 (dog.ceo API)
```javascript
fetch('https://dog.ceo/api/breeds/image/random')
  .then(resp => resp.json())
  .then(data => {
    document.getElementById('dogImg').innerHTML = `
      <img src="${data.message}" width="300px">
    `;
  });
```

### OpenAI API 요청 (인증 헤더 포함)
```javascript
fetch('https://api.openai.com/v1/models', {
  headers: {
    Authorization: 'Bearer YOUR_API_KEY'
  }
})
  .then(resp => resp.json())
  .then(data => console.log(data));
```

> 인증이 필요한 API는 `headers`에 `Authorization` 키를 넣어 보낸다.

---

## 7. 핵심 포인트 정리

| 개념 | 설명 |
|------|------|
| `fetch(url)` | GET 요청 (기본) |
| `response.ok` | 응답 상태가 200~299이면 `true` |
| `response.json()` | 응답 본문을 JSON으로 파싱 (Promise 반환) |
| `.then()` | 비동기 결과를 순서대로 처리 |
| `.catch()` | 모든 에러를 한 곳에서 처리 |
| `JSON.stringify()` | JS 객체 → JSON 문자열 (보낼 때) |
| `body` 옵션 | POST/PUT 시 보낼 데이터 |
| `headers` 옵션 | Content-Type, Authorization 등 설정 |

---

## 8. fetch 구조 한눈에 보기

```
fetch(URL, 옵션?)
  ├── method  : 'GET' | 'POST' | 'PUT' | 'DELETE'
  ├── headers : { 'Content-type': 'application/json' }
  └── body    : JSON.stringify(데이터)

응답 처리
  .then(response => response.json())   ← 파싱
  .then(data => { /* 사용 */ })        ← 활용
  .catch(error => { /* 처리 */ })      ← 에러
```
