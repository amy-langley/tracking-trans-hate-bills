from glob import glob
import logging
import os.path
import zipfile


logger = logging.getLogger(__name__)


def extract_one(zip_path: str, path: str):
    """Extract one zip file"""
    logger.debug(f'Unpacking {zip_path}')
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(path)

def extract_legiscan_datasets(work_dir: str) -> None:
    """Extract all zip files"""
    for zip_path in glob(os.path.join(work_dir, '*.zip')):
        extract_one(zip_path, work_dir)
