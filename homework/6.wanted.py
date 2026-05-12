from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(
        "https://www.wanted.co.kr/wdlist/518?country=kr&job_sort=job.popularity_order&years=0&locations=all"
    )

    job_posting = page.locator(".Card_Card__aaatv")
    print("채용공고 갯수: ", job_posting.count())

    # 이동할 채용 목록 관리
    links = []

    for i in range(job_posting.count()):
        jobs = job_posting.nth(i)

        # 제목 가져오기
        title = jobs.inner_text().strip()

        # 링크 가져오기

        href = jobs.locator(".JobCard_JobCard__aVx71 a").get_attribute("href")

        # print("링크:", href)

        links.append({"title": title, "href": href})

    for jobs in links:
        print("-" * 60)
        print("제목: ", jobs["title"])
        print("링크: ", jobs["href"])

        # 게시물로 이동
        page.goto("https://www.wanted.co.kr/" + jobs["href"])

        # 모집요강 추출
        content = page.locator(".JobDetail_jobDetail__si4a2").inner_text().strip()
        print("모집 요강: ", content)
