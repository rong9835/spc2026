from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://news.naver.com/section/105")

    headlines = page.locator(".section_article.as_headline a.sa_text_title")
    # print("헤드라인 갯수: ", headlines.count())

    # 이동할 뉴스 목록 관리
    links = []

    for i in range(headlines.count()):
        news = headlines.nth(i)

        # 제목 가져오기
        title = news.inner_text().strip()

        # 링크 가져오기
        href = news.get_attribute('href')

        links.append({
            "title": title,
            "href": href
        })

    for news in links:
        print("-"*60)
        print("제목: ", news["title"])
        print("링크: ", news["href"])

        # 게시물로 이동
        page.goto(news['href'])

        # 본문 추출
        content = page.locator("#dic_area").inner_text().strip()
        print("본문: ", content)
