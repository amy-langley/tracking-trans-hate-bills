from typing import Dict

from lib.util import load_json

def summarize_metadata(bill: Dict) -> Dict:
    """Generate summary data from a legiscan bill metadata blob"""
    return {
        'state': bill['state'],
        'bill_id': bill['bill_number'],
        'legiscan_bill_id': bill['bill_id'],
        'status_date': bill['status_date'],
        'title': bill['title'],
        'description': bill['description'].split('.')[0],
        'legiscan_doc_id': None if len(bill['texts']) < 1 else (
            sorted(
                bill['texts'],
                key=lambda t: t['date'],
                reverse=True
            )[0]['doc_id']
        ),
        'sponsors': [] if len(bill['sponsors']) < 1 else [
            sponsor['name']
            for sponsor
            in bill['sponsors']
        ],
    }


def summarize_metadata_file(json_path: str) -> Dict:
    """Summarize the file at the specified path"""
    bill = load_json(json_path)['bill']
    return summarize_metadata(bill)
