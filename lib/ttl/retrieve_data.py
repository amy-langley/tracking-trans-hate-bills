from bs4 import BeautifulSoup as Soup
from itertools import chain
import json
from pyjsparser import parse
import requests
import time
import typer
from urllib.parse import urljoin


URL = 'https://tracktranslegislation.com'
DEFAULT_OUTPUT_PATH = '../../datasets/tracktranslegislation.json'


def find_in_graph(subgraph):
    results = []
    items = subgraph.values() if isinstance(subgraph, dict) else subgraph
    local_results = (item for item in items if isinstance(item, str) and len(item) > 10000)
    return (chain.from_iterable([local_results, *(find_in_graph(item) for item in items if isinstance(item, dict) or isinstance(item,list))]))


def retrieve_ttl_data(output_path: str):
    page = requests.get(URL)
    soup = Soup(page.content, "html.parser")

    script_tags = soup.find_all('script')
    sources = [source_tag.attrs['src'] for source_tag in soup.find_all('script') if source_tag.has_attr('src')]
    quarry = urljoin(URL, next(source for source in sources if 'chunks/70-' in source))

    script_contents = requests.get(quarry).text

    parsed_script = parse(script_contents)
    candidates = find_in_graph(parsed_script)
    jsonstr = next(candidates)

    parsed_data = json.loads(jsonstr)

    with open(output_path, 'w') as outfile:
        json.dump(parsed_data, outfile, indent=2)
        
    return parsed_data


def main(output_path: str = typer.Argument(DEFAULT_OUTPUT_PATH)):
    start = time.time()
    contents = retrieve_ttl_data(output_path)
    end = time.time()

    print(f'Data "{output_path}" refreshed with {len(contents)} items ({(end-start):.2f}s elapsed)')
    
if __name__ == "__main__":
    typer.run(main)
