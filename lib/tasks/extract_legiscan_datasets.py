from glob import glob
import logging
import os.path
import zipfile


logger = logging.getLogger(__name__)


def extract_one(zip: str, path: str):
    logger.debug(f'Unpacking {zip}')
    with zipfile.ZipFile(zip, 'r') as zip_ref:
        zip_ref.extractall(path)

def extract_legiscan_datasets(work_dir: str) -> None:
    for zip in glob(os.path.join(work_dir, '*.zip')):
        extract_one(zip, work_dir)
