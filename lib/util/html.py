from bs4 import BeautifulSoup as Soup

def extract_html_text(file_path: str) -> str:
    soup = None
    with open(file_path, 'rb') as f:
        soup = Soup(f, 'html.parser')

    for script in soup(["script", "style"]):
        script.extract()

    return soup.get_text()
