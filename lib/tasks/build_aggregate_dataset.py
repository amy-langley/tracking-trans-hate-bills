import os.path

from glob import glob
from typing import List

import typer

from lib.legiscan import summarize_metadata_file
from lib.util import write_json

def build_aggregate_dataset(
    metadata_paths: List[str],
    output_path: str,
):
    """Consume all specified metadata files to produce a summarized dataset"""
    summaries = [
        summarize_metadata_file(metadata_file)
        for metadata_file
        in metadata_paths
    ]

    write_json(summaries, output_path)
    return summaries

def build_aggregate_dataset_from_path(
    metadata_path: str,
    output_path: str,
):
    """Find all metadata files in a path and use them to produce a summarized dataset"""
    all_metadata_files = glob(os.path.join(metadata_path, '*_meta_*.json'))
    return build_aggregate_dataset(all_metadata_files, output_path)

def main(
    metadata_paths: List[str],
    output_path: str,
):
    """The CLI for this task"""
    build_aggregate_dataset(metadata_paths, output_path)

if __name__ == "__main__":
    typer.run(main)
