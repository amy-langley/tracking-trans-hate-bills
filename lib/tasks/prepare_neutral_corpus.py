import pandas as pd
from typing import List


def select_neutral_corpus(summaries_file: str, corpus_size: int, *, filter_states: List[str]=[], random_state: int=1) -> pd.DataFrame:
    summaries = pd.read_json(summaries_file)
    candidates = summaries.apply(
        lambda x: (x['legiscan_doc_id'] is not None) and ((not filter_states) or x['state'] in filter_states),
        axis=1,
    )
    return summaries.loc[candidates].sample(n=corpus_size, random_state=random_state)
    

def prepare_neutral_corpus(work_dir: str, summaries_file: str, corpus_size: int, *, filter_states: List[str]=[], random_state: int=1): # -> None:
    return select_neutral_corpus(summaries_file, corpus_size, filter_states=filter_states, random_state=random_state)

