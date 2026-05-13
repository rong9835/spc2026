# Flask 정적 파일(Static Files) 핵심 정리

## 📁 프로젝트 폴더 구조

```
8.static/
├── 1.app.py                  ← Flask 서버 파일
├── static/                   ← 정적 파일 폴더 (CSS, 이미지, JS 등)
│   ├── css/
│   │   └── style.css
│   ├── img/
│   │   └── cat.png
│   └── user.html             ← 정적 HTML 파일
└── templates/                ← Jinja2 템플릿 폴더
    └── index.html            ← 동적 HTML 파일
```

---

## 1. 정적 파일 vs 템플릿 파일

| 구분 | 저장 위치 | 특징 | 반환 방법 |
|------|-----------|------|-----------|
| **정적 파일** | `static/` | 변하지 않는 HTML, CSS, 이미지 | `send_from_directory()` |
| **템플릿 파일** | `templates/` | Jinja2 문법 사용 가능, 동적 데이터 삽입 | `render_template()` |

---

## 2. app.py - 라우팅 핵심 코드

```python
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

# 템플릿 파일 반환 (templates/index.html)
@app.route('/')
def home():
    return render_template('index.html')

# 정적 파일 반환 (static/user.html)
@app.route('/user')
def user():
    return send_from_directory('static', 'user.html')

if __name__ == '__main__':
    app.run(debug=True)
```

### 핵심 함수 2가지

| 함수 | 용도 | 사용 예시 |
|------|------|-----------|
| `render_template('파일명')` | `templates/` 폴더의 HTML을 동적으로 렌더링 | `render_template('index.html')` |
| `send_from_directory('폴더', '파일명')` | 특정 폴더에서 파일을 그대로 전송 | `send_from_directory('static', 'user.html')` |

---

## 3. url_for() - 정적 파일 경로 생성

템플릿 파일(HTML)에서 CSS, 이미지 등 정적 파일을 불러올 때 사용

```html
<!-- CSS 불러오기 -->
<link href="{{ url_for('static', filename='css/style.css') }}" rel="stylesheet">

<!-- 이미지 불러오기 -->
<img src="{{ url_for('static', filename='img/cat.png') }}" alt="고양이사진">
```

> ⚠️ 하드코딩 대신 `url_for()` 사용을 권장  
> → 서버 경로가 바뀌어도 자동으로 올바른 URL 생성

### 직접 경로 vs url_for() 비교

```html
<!-- 비추천: 하드코딩 -->
<link href="/static/css/style.css" rel="stylesheet">

<!-- 추천: url_for() 사용 -->
<link href="{{ url_for('static', filename='css/style.css') }}" rel="stylesheet">
```

---

## 4. 정적 파일(static)의 자동 URL 접근

Flask는 `static/` 폴더 내 파일을 자동으로 `/static/파일명` 경로로 제공

```
http://localhost:5000/static/css/style.css
http://localhost:5000/static/img/cat.png
http://localhost:5000/static/user.html
```

별도 라우팅 없이도 접근 가능!

---

## 5. 전체 흐름 요약

```
브라우저 요청
    │
    ├── GET /          → render_template('index.html')
    │                     → templates/index.html 렌더링
    │                     → CSS, 이미지는 url_for()로 자동 참조
    │
    └── GET /user      → send_from_directory('static', 'user.html')
                          → static/user.html 파일 그대로 전송
```

---

## 6. 핵심 포인트 정리

- `static/` 폴더 → CSS, JS, 이미지, 정적 HTML 보관
- `templates/` 폴더 → Jinja2 문법을 쓰는 동적 HTML 보관
- `render_template()` → 템플릿 렌더링 (변수 전달 가능)
- `send_from_directory()` → 파일 직접 전송 (변수 전달 불가)
- `url_for('static', filename='...')` → 정적 파일 경로를 안전하게 생성
