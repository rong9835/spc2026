from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(
        "https://www.jobkorea.co.kr/Top100/?Main_Career_Type=1&Search_Type=1&BizJobtype_Bctgr_Code=10031&BizJobtype_Bctgr_Name=AI%C2%B7%EA%B0%9C%EB%B0%9C%C2%B7%EB%8D%B0%EC%9D%B4%ED%84%B0&BizJobtype_Code=0&BizJobtype_Name=AI%C2%B7%EA%B0%9C%EB%B0%9C%C2%B7%EB%8D%B0%EC%9D%B4%ED%84%B0+%EC%A0%84%EC%B2%B4&Major_Big_Code=0&Major_Big_Name=%EC%A0%84%EC%B2%B4&Major_Code=0&Major_Name=%EC%A0%84%EC%B2%B4&Edu_Level_Code=9&Edu_Level_Name=%EC%A0%84%EC%B2%B4&Edu_Level_Name=%EC%A0%84%EC%B2%B4&MidScroll=0"
    )

    job_posting = page.locator(".dmpItem")
    print("채용공고 갯수: ", job_posting.count())

    # # 이동할 채용 목록 관리
    links = []

    for i in range(job_posting.count()):
        jobs = job_posting.nth(i)

        # 제목 가져오기
        title = jobs.inner_text().strip()

        # 링크 가져오기

        href = jobs.locator(".link.dev-recruit-link").get_attribute("href")

        links.append({"title": title, "href": href})

    for jobs in links:
        print("-" * 60)
        print("제목: ", jobs["title"])
        print("링크: ", jobs["href"])

        # 게시물로 이동
        page.goto("https://www.jobkorea.co.kr" + jobs["href"])

        # 모집요강 추출
        content = (
            page.locator("[data-sentry-component='RecruitmentGuidelines']")
            .inner_text()
            .strip()
        )
        print("모집 요강: ", content)
