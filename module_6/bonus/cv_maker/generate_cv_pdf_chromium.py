"""HTML → PDF через Chromium (Playwright) — альтернатива wkhtmltopdf. Курс, М6, бонус «CV розробника».

wkhtmltopdf рендерить старим рушієм QtWebKit і більше не розвивається; Chromium — той самий рушій, що в
браузері, тож PDF виглядає так, як сторінка у Chrome (сучасний CSS: flexbox, grid, змінні).

    pip install playwright && playwright install chromium
    python generate_cv_pdf_chromium.py cv_template.html CV_Name_Surname.pdf

CHROMIUM_PATH — шлях до вже встановленого Chromium/Chrome, якщо `playwright install` зробити не можна.
"""
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent


def generate_pdf(html_file: str, output_pdf: str) -> Path:
    html_path = (BASE_DIR / html_file).resolve()
    output_path = BASE_DIR / output_pdf
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or None)
        page = browser.new_page()
        page.goto(html_path.as_uri())                  # file:// — локальні картинки й стилі теж підхопляться
        page.pdf(path=str(output_path), format="A4", print_background=True,
                 margin={"top": "15mm", "right": "15mm", "bottom": "15mm", "left": "15mm"})
        browser.close()
    print(f"PDF created: {output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: python generate_cv_pdf_chromium.py CV.html CV.pdf")
    generate_pdf(sys.argv[1], sys.argv[2])
