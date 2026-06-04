# 코드 취약점 분석기 (Code Vulnerability Analyzer)

> GitHub 코드를 붙여넣으면 AI가 보안 취약점을 찾아주는 웹 앱

---

## 이 프로젝트가 하는 일

```
사용자가 GitHub URL 입력
      ↓
서버가 GitHub에서 코드를 가져옴
      ↓
ChatGPT에게 "이 코드에서 보안 문제 찾아줘"라고 요청
      ↓
분석 결과를 화면에 출력
```

---

## 파일 구조

```
2.code_review/
├── app.py            ← 서버 (Flask, Python)
└── public/
    └── index.html    ← 화면 (HTML + JavaScript)
```

---

## 핵심 개념 정리

### 1. GitHub URL 변환 (`convert_github_url`)

GitHub에서 코드를 **직접 읽으려면** URL 형태를 바꿔야 해요.

| 구분 | URL 예시 |
|------|----------|
| 일반 GitHub 주소 | `github.com/user/repo/blob/main/app.py` |
| 코드 원문 주소 | `raw.githubusercontent.com/user/repo/refs/heads/main/app.py` |

```python
def convert_github_url(url):
    url = url.replace('github.com', 'raw.githubusercontent.com')
    url = url.replace('/blob/', '/refs/heads/')
    return url
```

> **비유**: 일반 GitHub 주소는 "책의 표지 페이지", raw 주소는 "책의 실제 내용 페이지"라고 생각하면 돼요.

---

### 2. API 엔드포인트 (`/api/codecheck`)

프론트(HTML)와 서버(Python)가 데이터를 주고받는 **창구**예요.

```
[브라우저]  →  POST /api/codecheck  →  [서버]
             { url, vulnerabilities }

[브라우저]  ←  JSON 응답            ←  [서버]
             { result, source_code }
```

**받는 데이터 (요청)**
- `url`: GitHub 파일 주소
- `vulnerabilities`: 체크한 취약점 목록 (예: `["SQL Injection", "XSS"]`)

**보내는 데이터 (응답)**
- `result`: ChatGPT 분석 결과
- `source_code`: 분석한 실제 코드

---

### 3. ChatGPT 프롬프트 구성

AI에게 질문할 때 **역할 + 명령 + 코드**를 함께 보내요.

```python
# 시스템 메시지: AI에게 역할 부여
{'role': 'system', 'content': '당신은 소스코드 분석 보안 전문가입니다.'}

# 유저 메시지: 실제 분석 요청
{'role': 'user', 'content': f'다음 소스코드에서 {vuln_list} 취약점을 분석하시오...'}
```

> **비유**: 시스템 메시지 = "너는 보안 전문가야", 유저 메시지 = "이 코드 분석해줘"

---

### 4. 프론트엔드 흐름 (JavaScript)

```javascript
// 1. 폼 제출 이벤트 감지
document.getElementById('myForm').addEventListener('submit', async (ev) => {
    ev.preventDefault();  // 페이지 새로고침 막기

    // 2. 체크된 취약점 목록 수집
    const vulnerabilities = [...document.querySelectorAll('input[type=checkbox]:checked')]
        .map((cb) => cb.value);

    // 3. 서버에 POST 요청
    const response = await fetch('/api/codecheck', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, vulnerabilities }),
    });

    // 4. 결과 화면에 출력
    const data = await response.json();
    result.innerText = data.result;
});
```

---

## 분석 가능한 취약점 3가지

| 취약점 | 설명 | 예시 |
|--------|------|------|
| **민감정보** | API 키, 비밀번호가 코드에 직접 쓰여 있는지 | `api_key = "sk-abc123"` |
| **SQL Injection** | 사용자 입력이 DB 쿼리에 그대로 들어가는지 | `"SELECT * WHERE id=" + user_input` |
| **XSS** | 사용자 입력이 HTML로 그대로 출력되는지 | `innerHTML = user_input` |

---

## 전체 흐름 요약

```
[index.html]
    ↓  GitHub URL + 체크박스 선택 후 "Check" 클릭
    ↓  fetch('/api/codecheck', { url, vulnerabilities })

[app.py - /api/codecheck]
    ↓  GitHub URL → raw URL로 변환
    ↓  requests.get(raw_url) → 코드 원문 가져오기
    ↓  프롬프트 조립 (취약점 목록 + 코드)
    ↓  client.chat.completions.create() → ChatGPT 요청

[ChatGPT (gpt-4o-mini)]
    ↓  보안 분석 결과 반환

[app.py]
    ↓  jsonify({ result, source_code }) 응답

[index.html]
    → 화면에 소스코드 + 분석 결과 출력
```

---

## 사용 기술

| 기술 | 역할 |
|------|------|
| **Flask** | Python 웹 서버 프레임워크 |
| **OpenAI API** | ChatGPT로 코드 분석 |
| **requests** | Python에서 외부 URL 요청 |
| **fetch API** | 브라우저에서 서버로 비동기 요청 |
| **dotenv** | `.env` 파일에서 API 키 불러오기 |
