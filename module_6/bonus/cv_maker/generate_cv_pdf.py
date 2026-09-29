from pathlib import Path
import shutil
import pdfkit


BASE_DIR = Path(__file__).resolve().parent


def find_wkhtmltopdf() -> str:
    from_path = shutil.which("wkhtmltopdf")

    if from_path:
        return from_path

    possible_paths = [
        r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
        r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
    ]

    for path in possible_paths:
        if Path(path).exists():
            return path

    raise FileNotFoundError(
        "wkhtmltopdf.exe не знайдено. "
        "Встанови wkhtmltopdf або перевір шлях до файлу."
    )


def generate_pdf(html_file: str, output_pdf: str) -> None:
    html_path = BASE_DIR / html_file
    output_path = BASE_DIR / output_pdf

    wkhtmltopdf_path = find_wkhtmltopdf()

    config = pdfkit.configuration(
        wkhtmltopdf=wkhtmltopdf_path
    )

    options = {
        "encoding": "UTF-8",
        "page-size": "A4",
        "margin-top": "15mm",
        "margin-right": "15mm",
        "margin-bottom": "15mm",
        "margin-left": "15mm",
        "enable-local-file-access": None,
    }

    pdfkit.from_file(
        str(html_path),
        str(output_path),
        configuration=config,
        options=options,
    )

    print(f"PDF created: {output_path}")


def main(html_file: str, output_pdf: str) -> None:
    generate_pdf(
        html_file=html_file,
        output_pdf=output_pdf,
    )


if __name__ == "__main__":
    # Курс, М6: свої файли — аргументами (python generate_cv_pdf.py cv_template.html CV_My_Name.pdf);
    # без аргументів — як у стартовому скрипті, CV викладача.
    import sys

    if len(sys.argv) == 3:
        main(html_file=sys.argv[1], output_pdf=sys.argv[2])
    else:
        main(
            html_file="cv_viktor_nikoriak_GeoAI.html",
            output_pdf="CV_Viktor_Nikoriak_GeoAI.pdf",
        )