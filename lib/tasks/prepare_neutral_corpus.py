import os.path

from math import isnan
from operator import itemgetter
from typing import List

import pandas as pd

from lib.legiscan import BillDescriptor, get_bill_text_direct, extract_bill_contents


def select_neutral_corpus(  # pylint: disable=W0102 # shut up shut up shut up
    summaries_file: str,
    corpus_size: int,
    *,
    filter_states: List[str]=[],
    random_state: int=1
) -> pd.DataFrame:
    """Select a random subset of the legiscan archive to build a neutral corpus"""
    summaries = pd.read_json(summaries_file)    # pylint: disable=E1101
    candidates = summaries.apply(               # pylint: disable=E1101
        lambda x: (
            (not isnan(x['legiscan_doc_id']))
            and ((not filter_states) or x['state'] in filter_states)
        ),
        axis=1,
    )
    return (
        summaries           # pylint: disable=E1101
        .loc[candidates]    # pylint: disable=E1101
        .sample(n=corpus_size, random_state=random_state)
    )


def prepare_neutral_corpus(  # pylint: disable=W0102
    work_dir: str,
    summaries_file: str,
    corpus_size: int,
    *,
    filter_states: List[str]=[],
    random_state: int=1
) -> List[str]:
    """Prepare a neutral corpus"""
    neutral_bills = select_neutral_corpus(
        summaries_file,
        corpus_size,
        filter_states=filter_states,
        random_state=random_state
    )

    tuples = (
        (
            BillDescriptor(
                *itemgetter(
                    'state',
                    'bill_id',
                    'legiscan_bill_id'
                )(neutral_bill)
            ),
            itemgetter('legiscan_doc_id')(neutral_bill)
        )
        for idx, neutral_bill
        in neutral_bills.iterrows()
    )

    responses = (
        (
            descriptor,
            get_bill_text_direct(  # pylint: disable=E1120
                descriptor,
                os.path.join(work_dir, 'metas'),
                str(doc_id),
            )
        )
        for descriptor, doc_id
        in tuples
    )

    return [
        extract_bill_contents(
            descriptor,
            os.path.join(work_dir, 'bills'),
            response_json,
        )
        for descriptor, response_json
        in responses
    ]
