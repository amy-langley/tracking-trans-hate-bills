import json
import logging
import time

from datetime import datetime, date
from typing import Any

from bs4 import BeautifulSoup as Soup
import requests
import typer

from lib.util import write_json

URL = "https://www.aclu.org/legislative-attacks-on-lgbtq-rights"
DEFAULT_OUTPUT_PATH = '../../datasets/aclu.json'
logger = logging.getLogger(__name__)


def sanitize_item(item):
    """Fix an item if it's corrupted"""
    broken = 'https://www.scstatehouse.gov/sess125_2023-2024/bills/585.htm'
    rewrite = (
        {'state': {'value': 'SC', 'label': 'South Carolina'}}
        if broken == item['link']
        else {}
    )
    return {
        **item,
        **rewrite
    }


# for some reason a few of the items in the dataset are from late 2022
def validate_date(item):
    """Decide whether a record is too old for us to consider"""
    return (
        datetime.strptime(item['status_date'], '%m/%d/%Y').date()
        > date.fromisoformat('2023-01-01')
    )


def retrieve_aclu_data(output_path: str):
    """Download the ACLU dataset"""
    page = requests.get(URL, timeout=30)
    soup: Any = Soup(page.content, "html.parser")
    bills = soup.find(id='map').find_all('legtracker')[0][':bills']
    contents = [sanitize_item(item) for item in json.loads(bills) if validate_date(item)]

    write_json(contents, output_path)

    return contents


def main(
    output_path: str = typer.Argument(DEFAULT_OUTPUT_PATH)
):
    """The CLI for this task"""
    start = time.time()
    contents = retrieve_aclu_data(output_path)
    end = time.time()

    logger.info(
        f'Data "{output_path}" refreshed with'
        f'{len(contents)} items ({(end-start):.2f}s elapsed)'
    )

if __name__ == "__main__":
    typer.run(main)
