from playwright.sync_api import sync_playwright


def analyze_form(url):
    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        page = browser.new_page()

        page.goto(url)

        print("\n===== FORM ANALYSIS =====")

        inputs = page.locator("input").all()

        print("\nINPUT FIELDS:")

        for index, element in enumerate(inputs):
            try:
                print(
                    index + 1,
                    "| type:",
                    element.get_attribute("type"),
                    "| name:",
                    element.get_attribute("name"),
                    "| placeholder:",
                    element.get_attribute("placeholder")
                )
            except:
                pass

        textareas = page.locator("textarea").all()

        print("\nTEXTAREAS:")

        for index, element in enumerate(textareas):
            try:
                print(
                    index + 1,
                    "| name:",
                    element.get_attribute("name"),
                    "| placeholder:",
                    element.get_attribute("placeholder")
                )
            except:
                pass

        selects = page.locator("select").all()

        print("\nSELECT DROPDOWNS:")

        for index, element in enumerate(selects):
            try:
                print(
                    index + 1,
                    "| name:",
                    element.get_attribute("name")
                )
            except:
                pass

        buttons = page.locator("button").all()

        print("\nBUTTONS:")

        for index, element in enumerate(buttons):
            try:
                print(
                    index + 1,
                    "|",
                    element.inner_text()
                )
            except:
                pass

        print("\n========================")

        page.wait_for_timeout(10000)

        browser.close()


if __name__ == "__main__":
    
    analyze_form("http://127.0.0.1:8000/frontend/test_application.html")