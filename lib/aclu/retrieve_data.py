from bs4 import BeautifulSoup as Soup
from datetime import datetime, date
import json
import logging
import requests
import time
import typer


URL = "https://www.aclu.org/legislative-attacks-on-lgbtq-rights"
DEFAULT_OUTPUT_PATH = '../../datasets/aclu.json'


def sanitize_item(item):
    broken = 'https://www.scstatehouse.gov/sess125_2023-2024/bills/585.htm'
    rewrite = {'state': {'value': 'SC', 'label': 'South Carolina'}} if broken == item['link'] else {}
    return {
        **item,
        **rewrite
    }


# for some reason a few of the items in the dataset are from late 2022
def validate_date(item):
    return datetime.strptime(item['status_date'], '%m/%d/%Y').date() > date.fromisoformat('2023-01-01')


def retrieve_aclu_data(output_path: str):
    page = requests.get(URL)
    soup = Soup(page.content, "html.parser")
    bills = soup.find(id='map').find_all('legtracker')[0][':bills']
    contents = [sanitize_item(item) for item in json.loads(bills) if validate_date(item)]

    with open(output_path, 'w') as outfile:
        json.dump(contents, outfile, indent=2)
    
    return contents


def main(output_path: str = typer.Argument(DEFAULT_OUTPUT_PATH)):
    start = time.time()
    contents = retrieve_aclu_data(output_path)
    end = time.time()

    print(f'Data "{output_path}" refreshed with {len(contents)} items ({(end-start):.2f}s elapsed)')
    
if __name__ == "__main__":
    typer.run(main)
