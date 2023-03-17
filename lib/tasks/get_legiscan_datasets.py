from bs4 import BeautifulSoup as Soup
from collections import namedtuple
from lib.legiscan import make_legiscan_session
import os.path
from urllib.parse import urljoin


Dataset = namedtuple("Dataset", "state year session modified exported json_url csv_url")

 
LEGISCAN_ROOT = 'https://legiscan.com'


def get_datasets_html(session) -> str:
    return session.get(urljoin(LEGISCAN_ROOT, 'datasets')).text


def retrieve_archive(json_url: str, work_dir: str, session, *, force: bool = False) -> None:
    local_filename = '-'.join(os.path.basename(json_url).split('_')[0:3]) + '.zip'
    local_path = os.path.join(work_dir, local_filename)
    
    if os.path.exists(local_path) and not force:
        print(f'{local_filename} already exists')
        return

    with open(local_path, 'wb') as f:
        f.write(session.get(urljoin(LEGISCAN_ROOT, json_url)).content)

    print(f'Created archive {local_filename}')

    
def get_legiscan_datasets(work_dir: str, year: str='2023', *, force: bool = False) -> None:
    with make_legiscan_session() as session:
        soup = Soup(get_datasets_html(session), 'html.parser')
        dataset_table = soup.find(id='gaits-datasets')
        table_data = [
            Dataset(*(
                cell.text if len(cell.find_all('a'))<1 else cell.find_all('a')[0].attrs['href']
                for cell 
                in row.find_all('td')))
            for row
            in dataset_table.find_all('tbody')[0].find_all('tr')
        ]

        [retrieve_archive(item.json_url, work_dir, session, force=force) for item in table_data if year in item.session]
