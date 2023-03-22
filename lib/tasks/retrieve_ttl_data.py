import json
import logging
import time

from itertools import chain
from urllib.parse import urljoin

import requests

from bs4 import BeautifulSoup as Soup
from pyjsparser import parse
import typer

from lib.util import write_json

URL = 'https://tracktranslegislation.com'
DEFAULT_OUTPUT_PATH = '../../datasets/tracktranslegislation.json'
logger = logging.getLogger(__name__)


def find_in_graph(subgraph):
    """Try to locate long strings somewhere in the parse tree"""
    items = subgraph.values() if isinstance(subgraph, dict) else subgraph
    local_results = (item for item in items if isinstance(item, str) and len(item) > 10000)
    return (chain.from_iterable([
        local_results, *(find_in_graph(item)
                            for item
                            in items
                            if isinstance(item, dict) or isinstance(item,list))]))


def retrieve_ttl_data(output_path: str):
    """Intercept the TTL dataset"""
    page = requests.get(URL, timeout=30)
    soup = Soup(page.content, "html.parser")

    sources = [
        source_tag.attrs['src']
        for source_tag
        in soup.find_all('script')
        if source_tag.has_attr('src')
    ]
    quarry = urljoin(URL, next(source for source in sources if 'chunks/70-' in source))

    script_contents = requests.get(quarry, timeout=30).text

    parsed_script = parse(script_contents)
    candidates = find_in_graph(parsed_script)
    jsonstr = next(candidates)

    parsed_data = json.loads(jsonstr)

    write_json(parsed_data, output_path)

    return parsed_data


def main(
    output_path: str = typer.Argument(DEFAULT_OUTPUT_PATH)
):
    """The CLI for this task"""
    start = time.time()
    contents = retrieve_ttl_data(output_path)
    end = time.time()

    logger.info(
        f'Data "{output_path}" refreshed with'
        f'{len(contents)} items ({(end-start):.2f}s elapsed)'
    )

if __name__ == "__main__":
    typer.run(main)
