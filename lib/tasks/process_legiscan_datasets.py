from glob import glob
import logging

import typer

from lib.legiscan import summarize_metadata_file
from lib.util import write_json


logger = logging.getLogger(__name__)


def process_legiscan_datasets(work_dir: str, output_path: str) -> None:
    """Generate summaries from legiscan archival data"""
    summaries = [
        summarize_metadata_file(bill)
        for bill
        in glob(f'{work_dir}/*/*/bill/*.json')
    ]

    write_json(summaries, output_path)

def main(
    corpus_path: str,
    summary_path: str,
):
    """The CLI for this task"""
    process_legiscan_datasets(corpus_path, summary_path)

if __name__ == "__main__":
    typer.run(main)
