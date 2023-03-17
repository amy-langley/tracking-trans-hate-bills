from glob import glob
import os.path
import zipfile

def extract_one(zip: str, path: str):
    print(f'Unpacking {zip}')
    with zipfile.ZipFile(zip, 'r') as zip_ref:
        zip_ref.extractall(path)

def extract_legiscan_datasets(work_dir: str) -> None:
    for zip in glob(os.path.join(work_dir, '*.zip')):
        extract_one(zip, work_dir)
