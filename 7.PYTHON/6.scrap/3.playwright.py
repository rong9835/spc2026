# pip install playwright
# playwright install  <-- 각종 브라우저 드라이버를 관리
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # 크롬을 실행한다
    browser = p.chromium.launch(headless=False)

    # 빈 페이지를 띄운다
    page = browser.new_page()

    # 원하는 사이트로 가게한다
    page.goto("https://www.naver.com")
    
    print(page.title())

    page.screenshot(path="naver.png")

    input("엔터를 누르면 종료됩니다")