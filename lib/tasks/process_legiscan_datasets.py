from glob import glob
import json
import logging
from typing import Dict

from lib.legiscan import summarize_metadata_file
from lib.util import load_json, write_json


logger = logging.getLogger(__name__)


def process_legiscan_datasets(work_dir: str, output_path: str) -> None:
    summaries = [
        summarize_metadata_file(bill)
        for bill
        in glob(f'{work_dir}/*/*/bill/*.json')
    ]
    
    write_json(summaries, output_path)
