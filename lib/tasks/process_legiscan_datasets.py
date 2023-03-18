from glob import glob
import json
import logging
from typing import Dict


logger = logging.getLogger(__name__)


def summarize_one(json_path: str) -> Dict:
    logger.debug(f'Summarizing {json_path}')
    bill = None
    with open(json_path, 'r') as f:
        bill = json.load(f)['bill']
        
    return {
        'state': bill['state'],
        'bill_id': bill['bill_number'],
        'legiscan_bill_id': bill['bill_id'],
        'status_date': bill['status_date'],
        'title': bill['title'],
        'description': bill['description'],
        'legiscan_doc_id': None if len(bill['texts']) < 1 else (
            sorted(
                bill['texts'], 
                key=lambda t: t['date'], 
                reverse=True
            )[0]['doc_id']
        )
    }


def process_legiscan_datasets(work_dir: str, output_path: str) -> None:
    summaries = [
        summarize_one(bill)
        for bill
        in glob(f'{work_dir}/*/*/bill/*.json')
    ]
    
    with open(output_path, 'w') as f:
        json.dump(summaries, f, indent=2)
