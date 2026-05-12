from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://books.toscrape.com/")

    # 책 목록을 가져오기
    books = page.locator("article.product_pod")
    # print(books.count())

    for i in range(books.count()):
        book = books.nth(i)

        title = book.locator("h3 a").get_attribute('title')
        print(title)

        price = book.locator(".price_color").inner_text()
        price = price.replace("£", "")
        print(price)

        rating = book.locator("p.star-rating").get_attribute("class")
        rating = rating.split()[-1]
        print(rating)