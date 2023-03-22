import pdfplumber

def extract_pdf_text(file_path: str) -> str:
    """Extract usable text from a pdf file"""
    text = ''

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = text + "\n" + page.extract_text()

    return text
