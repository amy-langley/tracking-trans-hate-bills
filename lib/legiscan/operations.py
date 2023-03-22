from enum import IntEnum
from typing import Dict

from lib.util import load_json

class LegiscanStatus(IntEnum):
    """This is from the legiscan manual"""
    # pragma pylint: disable=C0103
    NA = 0
    Introduced = 1
    Engrossed = 2
    Enrolled = 3
    Passed = 4
    Vetoed = 5
    Failed = 6
    Override = 7
    Chaptered = 8
    Refer = 9
    Report_Pass = 10
    Report_DNP = 11
    Draft = 12


def summarize_metadata(bill: Dict) -> Dict:
    """Generate summary data from a legiscan bill metadata blob"""
    return {
        'state': bill['state'],
        'bill_id': bill['bill_number'],
        'legiscan_bill_id': bill['bill_id'],
        'status': str(LegiscanStatus(bill['status'])).split('.')[1],
        'status_date': bill['status_date'],
        'introduced_date': str(sorted(
            bill['history'],
            key=lambda t: t['date'],
        )[0]['date']) if bill['history'] else None,
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
