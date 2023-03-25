from math import isnan
from operator import itemgetter
from typing import List

import pandas as pd
import typer

from lib.legiscan import BillDescriptor, download_and_extract


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

    return [
        download_and_extract(  # pylint: disable=E1120
            descriptor,
            str(int(doc_id)),
            work_dir,
        )
        for descriptor, doc_id
        in tuples
    ]


def main(
    summaries_path: str,
    aggregate_path: str,
    output_path: str,
    num_bills: int = typer.Option(10),
    random_state: int = typer.Option(1),
):
    """The CLI for this task"""
    aggregate_frame = pd.read_json(aggregate_path)
    states_with_bills = aggregate_frame.state.unique().tolist()  # pylint: disable=E1101
    prepare_neutral_corpus(
        output_path,
        summaries_path,
        num_bills,
        filter_states=states_with_bills,
        random_state=random_state
    )


if __name__ == "__main__":
    typer.run(main)
