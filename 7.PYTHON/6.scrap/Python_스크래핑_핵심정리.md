# Python 웹 스크래핑 핵심 정리

## 스크래핑이란?

웹사이트의 HTML을 가져와서 원하는 데이터만 추출하는 기술.

```
웹사이트 → HTML 다운로드 → 파싱(분석) → 데이터 추출
```

---

## 방법 1: requests + BeautifulSoup (정적 페이지)

### 언제 사용하나?
- 서버에서 HTML을 바로 내려주는 **정적 페이지**에 사용
- JavaScript로 동적으로 그려지는 페이지에는 사용 불가

### 필요한 라이브러리

```bash
pip install requests beautifulsoup4
```

### 기본 흐름

```python
import requests
from bs4 import BeautifulSoup

# 1. 페이지 다운로드
resp = requests.get("https://books.toscrape.com")
resp.encoding = "utf-8"  # 한글 깨짐 방지

# 2. HTML 파싱 (분석)
soup = BeautifulSoup(resp.text, "html.parser")

# 3. 원하는 요소 선택
books = soup.select("article.product_pod")

# 4. 데이터 추출
for book in books:
    title = book.h3.a["title"]          # 속성값 가져오기
    price = book.select_one(".price_color").text  # 텍스트 가져오기
```

### 요소 선택 방법

| 메서드 | 설명 | 예시 |
|--------|------|------|
| `soup.select("선택자")` | CSS 선택자로 **여러 개** 찾기 | `soup.select("article.product_pod")` |
| `soup.select_one("선택자")` | CSS 선택자로 **첫 번째 하나**만 찾기 | `soup.select_one(".price_color")` |
| `soup.find_all("태그", class_="클래스")` | 태그 + 클래스로 여러 개 찾기 | `soup.find_all("article", class_="product_pod")` |

### 데이터 추출 방법

```python
element = soup.select_one(".price_color")

element.text          # 태그 안의 텍스트
element["href"]       # 속성값 (href, title, class 등)
element["class"][1]   # class는 리스트 → 인덱스로 접근
element.inner_text()  # 내부 텍스트 (공백 포함)
```

### 실습: 도서 정보 수집 후 CSV 저장

```python
import requests
from bs4 import BeautifulSoup
import csv

url = "https://books.toscrape.com"
resp = requests.get(url)
resp.encoding = "utf-8"

soup = BeautifulSoup(resp.text, "html.parser")
books = soup.select("article.product_pod")

# 영어 평점 → 숫자 변환
rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

with open("books.csv", "w", encoding="utf-8", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["도서명", "평점", "가격"])  # 헤더

    for book in books:
        title = book.h3.a["title"]
        rating = rating_map[book.p["class"][1]]
        price = book.select_one(".price_color").text.replace("£", "")

        writer.writerow([title, rating, price])
```

---

## 방법 2: Playwright (동적 페이지)

### 언제 사용하나?
- JavaScript로 데이터를 **동적으로 렌더링**하는 페이지
- 로그인, 버튼 클릭, 스크롤 등 **사용자 동작이 필요한** 경우
- 네이버, 유튜브 등 SPA(Single Page Application) 사이트

### 설치

```bash
pip install playwright
playwright install   # 크롬, 파이어폭스 등 브라우저 드라이버 설치
```

### 기본 흐름

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # 1. 브라우저 실행
    browser = p.chromium.launch(headless=False)  # False = 창 보임

    # 2. 새 탭(페이지) 열기
    page = browser.new_page()

    # 3. 사이트 이동
    page.goto("https://www.naver.com")

    # 4. 스크린샷 저장
    page.screenshot(path="naver.png")

    print(page.title())  # 페이지 제목
```

### headless 옵션

```python
browser = p.chromium.launch(headless=False)  # 브라우저 창 보임 (디버깅용)
browser = p.chromium.launch(headless=True)   # 브라우저 숨김 (배포용)
```

### 요소 선택 및 데이터 추출

```python
# CSS 선택자로 요소 찾기
books = page.locator("article.product_pod")

# 개수 확인
print(books.count())

# 인덱스로 개별 요소 접근
for i in range(books.count()):
    book = books.nth(i)

    title = book.locator("h3 a").get_attribute("title")  # 속성값
    price = book.locator(".price_color").inner_text()     # 텍스트
    rating = book.locator("p.star-rating").get_attribute("class")  # class 속성
```

### requests vs Playwright 비교

| | requests + BeautifulSoup | Playwright |
|---|---|---|
| **속도** | 빠름 | 느림 (브라우저 실행) |
| **정적 페이지** | ✅ 사용 가능 | ✅ 사용 가능 |
| **동적 페이지 (JS)** | ❌ 불가 | ✅ 사용 가능 |
| **로그인/클릭** | ❌ 불가 | ✅ 사용 가능 |
| **설치 난이도** | 쉬움 | 보통 |

---

## 실습: 네이버 뉴스 본문까지 수집

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://news.naver.com/section/105")

    # 헤드라인 링크 요소들 선택
    headlines = page.locator(".section_article.as_headline a.sa_text_title")

    # 먼저 링크 목록을 수집 (페이지 이동 전에!)
    links = []
    for i in range(headlines.count()):
        news = headlines.nth(i)
        links.append({
            "title": news.inner_text().strip(),
            "href": news.get_attribute("href")
        })

    # 각 기사로 이동해서 본문 수집
    for news in links:
        print("-" * 60)
        print("제목:", news["title"])
        page.goto(news["href"])           # 기사 페이지로 이동
        content = page.locator("#dic_area").inner_text().strip()
        print("본문:", content)
```

> **주의**: 링크 수집과 페이지 이동을 분리해야 한다.  
> 페이지가 바뀌면 기존에 찾아둔 `locator`가 무효화되기 때문!

---

## CSV 파일 저장

```python
import csv

with open("파일명.csv", "w", encoding="utf-8", newline="") as file:
    writer = csv.writer(file)
    
    # 헤더 행
    writer.writerow(["컬럼1", "컬럼2", "컬럼3"])
    
    # 데이터 행
    writer.writerow(["값1", "값2", "값3"])
```

| 옵션 | 설명 |
|------|------|
| `"w"` | 쓰기 모드 (덮어쓰기) |
| `encoding="utf-8"` | 한글 깨짐 방지 |
| `newline=""` | 윈도우에서 빈 줄 생기는 것 방지 |

---

## 자주 쓰는 문자열 정리

```python
text.strip()           # 앞뒤 공백 제거
text.replace("£", "")  # 특정 문자 제거 (빈 문자로 교체)
text.split()[-1]       # 공백 기준으로 나눠서 마지막 요소 가져오기

# 예시: "star-rating Three" → "Three"
rating = "star-rating Three"
rating.split()[-1]  # → "Three"
```

---

## 핵심 요약

```
정적 페이지 → requests + BeautifulSoup
동적 페이지 → Playwright

데이터 선택 → CSS 선택자 활용 (select, locator)
데이터 저장 → CSV 파일 (csv 모듈)
```
