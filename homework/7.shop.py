from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://makemyproject.net/shop/")
    page.wait_for_selector(".card")
    shop_titles = page.locator(".card")
    # print("목록개수:", shop_titles.count())

    # 이동할 채용 목록 관리
    links = []

    for i in range(shop_titles.count()):
        products = shop_titles.nth(i)

        # 제목 가져오기
        title = products.inner_text().strip()

        # 링크 가져오기

        href = products.locator("a").get_attribute("href")

        print("링크:", href)

        links.append({"title": title, "href": href})

    for products in links:
        print("-" * 60)
        print("제목: ", products["title"])
        print("링크: ", products["href"])

        # 게시물로 이동
        page.goto("https://makemyproject.net/shop/" + products["href"])

        # 상품설명 추출
        product_content = page.locator("div.muted").first.inner_text().strip()
        print("상품 설명: ", product_content)

        # 구매량 추출
        order_count = page.locator("#sales").inner_text().strip()
        print("구매량: ", order_count)

        # 상품후기 추출
        reviews = page.locator(".review").all_inner_texts()
        for review in reviews:
            print("상품 후기: ", review.strip())
