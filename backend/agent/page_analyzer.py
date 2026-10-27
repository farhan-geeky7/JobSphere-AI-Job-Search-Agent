from playwright.sync_api import sync_playwright


def analyze_page(url):
    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        page = browser.new_page()

        page.goto(url)

        print("\n===== PAGE ANALYSIS =====")

        print("Title:")
        print(page.title())

        print("\nURL:")
        print(page.url)

        print("\nVisible Text:")
        text = page.locator("body").inner_text()
        print(text[:5000])

        print("\nLinks:")
        links = page.locator("a").all()

        for index, link in enumerate(links[:20]):
            try:
                print(
                    index + 1,
                    "|",
                    link.inner_text(),
                    "|",
                    link.get_attribute("href")
                )
            except:
                pass

        print("\nButtons:")

        buttons = page.locator("button").all()

        for index, button in enumerate(buttons[:20]):
            try:
                print(
                    index + 1,
                    "|",
                    button.inner_text()
                )
            except:
                pass

        print("\n=========================")

        page.wait_for_timeout(10000)

        browser.close()


if __name__ == "__main__":
    analyze_page("https://example.com")