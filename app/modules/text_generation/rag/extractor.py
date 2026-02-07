from pypdf import PdfReader


def pdf_text_extractor(filepath: str) -> None:
    content = ""
    pdf = PdfReader(filepath, strict=True)

    for page in pdf.pages:
        if page_text := page.extract_text():
            content += f"{page_text}\n\n"

    with open(filepath.replace("pdf", "txt"), "w", encoding="utf-8") as file:
        file.write(content)
