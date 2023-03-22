from bs4 import BeautifulSoup as Soup

def extract_html_text(file_path: str) -> str:
    """Extract usable text from an html file"""
    soup = None
    with open(file_path, 'rb') as source:
        soup = Soup(source, 'html.parser')

    for script in soup(["script", "style"]):
        script.extract()

    return soup.get_text()
