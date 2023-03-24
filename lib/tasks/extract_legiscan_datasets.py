from glob import glob
import logging
import os.path
import zipfile

from typing import Optional

import typer


logger = logging.getLogger(__name__)


def extract_one(zip_path: str, path: str):
    """Extract one zip file"""
    logger.debug(f'Unpacking {zip_path}')
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(path)

def extract_legiscan_datasets(work_dir: str, output_path: Optional[str] = None) -> None:
    """Extract all zip files"""
    output_path = output_path or work_dir
    for zip_path in glob(os.path.join(work_dir, '*.zip')):
        extract_one(zip_path, output_path)

def main(
    archive_dir: str,
    output_path: str
):
    """The CLI for this task"""
    extract_legiscan_datasets(archive_dir, output_path)

if __name__ == "__main__":
    typer.run(main)
