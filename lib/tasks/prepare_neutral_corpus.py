from math import isnan
from operator import itemgetter
import pandas as pd
from typing import List

from lib.legiscan import BillDescriptor, get_bill_text_direct, extract_bill_contents


def select_neutral_corpus(summaries_file: str, corpus_size: int, *, filter_states: List[str]=[], random_state: int=1) -> pd.DataFrame:
    summaries = pd.read_json(summaries_file)
    candidates = summaries.apply(
        lambda x: (not isnan(x['legiscan_doc_id'])) and ((not filter_states) or x['state'] in filter_states),
        axis=1,
    )
    return summaries.loc[candidates].sample(n=corpus_size, random_state=random_state)
    

def prepare_neutral_corpus(work_dir: str, summaries_file: str, corpus_size: int, *, filter_states: List[str]=[], random_state: int=1): # -> List[str]:
    neutral_bills = select_neutral_corpus(summaries_file, corpus_size, filter_states=filter_states, random_state=random_state)

    tuples = (
        (
            BillDescriptor(*itemgetter('state', 'bill_id', 'legiscan_bill_id')(neutral_bill)), 
            itemgetter('legiscan_doc_id')(neutral_bill)
        )
        for idx, neutral_bill
        in neutral_bills.iterrows()
    )
    
    responses = (
        (descriptor, get_bill_text_direct(descriptor, '../tmp/neutral_corpus/metas', str(doc_id)))
        for descriptor, doc_id
        in tuples
    )
    
    return [
        extract_bill_contents(descriptor, '../tmp/neutral_corpus/bills', response_json)
        for descriptor, response_json
        in responses
    ]
