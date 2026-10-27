from playwright.sync_api import sync_playwright


def start_browser():
    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        page = browser.new_page()

        page.goto("https://example.com")

        print("Browser started successfully")
        print("Page title:", page.title())
        print("Page URL:", page.url)

        page.wait_for_timeout(60000)

        browser.close()


if __name__ == "__main__":
    start_browser()