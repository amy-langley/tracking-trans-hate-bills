from itertools import chain
from typing import Iterable, List

import typer

from lib.language import tokenize_file
from lib.util import write_json


def tokenize_bills(
    bill_filenames: Iterable[str],
) -> Iterable[str]:
    """Produce a unified token stream from a list of files"""
    all_tokens = list(chain.from_iterable(
        tokenize_file(bill_filename)
        for bill_filename
        in bill_filenames
    ))

    return all_tokens

def main(
    bill_filenames: List[str],
    output_filename: str,
):
    """The CLI for this task"""
    all_tokens = tokenize_bills(bill_filenames)
    write_json(list(all_tokens), output_filename)

if __name__ == "__main__":
    typer.run(main)
