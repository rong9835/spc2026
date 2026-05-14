# async / await 핵심 요약

## 1. async/await 란?

`Promise`를 더 읽기 쉽게 쓰는 **문법 설탕(Syntactic Sugar)**

```
기존 방식 (Promise 체인)        async/await 방식
─────────────────────────      ─────────────────────────
fetch(url)                     const response = await fetch(url)
  .then(res => res.json())     const data = await response.json()
  .then(data => ...)           // 이후 로직...
  .catch(err => ...)
```

> 실행 방식은 동일하지만, 위에서 아래로 읽히는 **동기 코드처럼** 보여서 훨씬 직관적

---

## 2. 기본 문법

```javascript
// async 키워드 → 이 함수 안에서 await를 쓸 수 있게 선언
async function getData() {

  // await 키워드 → Promise가 완료될 때까지 여기서 기다림
  const response = await fetch('https://...')

  const data = await response.json()
  return data
}
```

### 핵심 규칙
| 규칙 | 설명 |
|------|------|
| `async` 없이 `await` 불가 | `await`는 반드시 `async` 함수 안에서만 사용 |
| `await`는 Promise를 기다림 | Promise가 아닌 값엔 써도 되지만 의미 없음 |
| `async` 함수는 항상 Promise 반환 | 내부에서 `return 1` 해도 `Promise<1>` 이 됨 |

---

## 3. 오류 처리 — try / catch

`Promise` 체인의 `.catch()` 역할을 `try/catch`가 대신함

```javascript
async function loadData() {
  try {
    const response = await fetch('https://...')

    // ① 네트워크는 성공했으나 HTTP 상태가 실패(4xx, 5xx)인 경우
    if (!response.ok) {
      throw new Error('요청 실패: ' + response.status)
    }

    const data = await response.json()
    return data

  } catch (error) {
    // ② 네트워크 오류 or 위에서 throw 한 오류 모두 여기서 잡힘
    console.error('오류 발생:', error)
  }
}
```

### response.ok 를 꼭 확인해야 하는 이유

```
fetch는 서버에서 404, 500 응답이 와도 reject(오류) 하지 않는다!
오직 네트워크 자체가 끊길 때만 catch 로 간다.

따라서 response.ok (상태코드 200~299 여부) 를 직접 체크해야 한다.
```

---

## 4. 실습 흐름 정리

### 실습 2 — 기본 fetch (콘솔 출력)
```javascript
// 버튼 클릭 → 데이터 요청 → 콘솔에 출력
document.getElementById('loadBtn').addEventListener('click', async () => {
  try {
    const response = await fetch('https://jsonplaceholder.typicode.com/todos/1')
    if (!response.ok) throw new Error('오류')
    const data = await response.json()
    console.log(data)  // { id, title, completed, userId }
  } catch (error) {
    console.log(error)
  }
})
```

### 실습 3 — DOM에 렌더링
```javascript
const data = await response.json()

// 받아온 데이터를 HTML로 만들어 화면에 표시
document.getElementById('result').innerHTML = `
  <ul>
    <li>Id: ${data.id}</li>
    <li>Title: ${data.title}</li>
  </ul>
`
```

### 실습 4 — 사용자 입력값으로 동적 요청
```javascript
// 입력창의 값을 읽어서 URL에 삽입 → 동적 API 요청
const userid = document.getElementById('uid').value

const response = await fetch(`https://jsonplaceholder.typicode.com/users/${userid}`)
const data = await response.json()

// 중첩 리스트로 상세 정보 표시
document.getElementById('result').innerHTML = `
  <ul>
    <li>사용자ID: ${data.id}</li>
    <ul>
      <li>이름: ${data.name}</li>
      <li>전화번호: ${data.phone}</li>
      <li>웹사이트: ${data.website}</li>
    </ul>
  </ul>
`
```

---

## 5. fetch 전체 흐름 한눈에 보기

```
버튼 클릭
    │
    ▼
fetch(url)  ──── 네트워크 오류 ────▶ catch (오류 처리)
    │
    ▼ (응답 도착)
response.ok 확인
    │ false → throw new Error → catch
    │ true
    ▼
response.json()  ──── 파싱 오류 ──▶ catch
    │
    ▼ (data 완성)
DOM 업데이트 or 로직 실행
```

---

## 6. Promise 체인 vs async/await 비교

```javascript
// ── Promise 체인 ──────────────────────────────
fetch(url)
  .then(res => {
    if (!res.ok) throw new Error('실패')
    return res.json()
  })
  .then(data => {
    // 데이터 처리
  })
  .catch(err => console.error(err))


// ── async/await (같은 동작) ──────────────────
async function load() {
  try {
    const res = await fetch(url)
    if (!res.ok) throw new Error('실패')
    const data = await res.json()
    // 데이터 처리
  } catch (err) {
    console.error(err)
  }
}
```

> 로직이 복잡해질수록 async/await 가 압도적으로 읽기 쉽다.

---

## 7. 핵심 키워드 한줄 정리

| 키워드 | 한줄 설명 |
|--------|-----------|
| `async` | 이 함수는 비동기 함수입니다 (await 사용 허가) |
| `await` | Promise가 끝날 때까지 여기서 멈추고 기다려 |
| `fetch()` | 외부 서버에 HTTP 요청을 보내는 내장 함수 |
| `response.ok` | HTTP 상태코드가 200~299 이면 `true` |
| `response.json()` | 응답 body를 JSON으로 파싱 (이것도 Promise!) |
| `try/catch` | 비동기 오류를 동기 코드처럼 잡는 방법 |
| `throw new Error()` | 오류를 직접 발생시켜 catch 블록으로 보냄 |
