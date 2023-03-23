from operator import itemgetter
from typing import Dict, Iterable, List, Optional, Tuple

import typer

from lib.legiscan import BillDescriptor, download_and_extract
from lib.util import load_json

def wrangle_metadata(metadata: Dict) -> Tuple[BillDescriptor, Optional[str]]:
    """Get the stuff from a metadata blob that we need to download a piece of legislation"""
    descriptor = BillDescriptor(*itemgetter('state', 'bill_number', 'bill_id')(metadata))
    doc_id =  None if len(metadata['texts']) < 1 else (
        sorted(
            metadata['texts'],
            key=lambda t: t['date'],
            reverse=True
        )[0]['doc_id']
    )

    return (descriptor, doc_id)

def retrieve_legislation(
    metadata_files: Iterable[str],
    output_path: str,
) -> List[str]:
    """Retrieve contents of legislation specified by each metadata file"""
    download_args = (
        (
            *wrangle_metadata(load_json(metadata_filename)['bill']),
            output_path
        )
        for metadata_filename
        in metadata_files
    )

    return [
        download_and_extract(*arg)
        for arg
        in download_args
        if arg[1]
    ]

def main(
    metadata_files: List[str],
    output_path: str,
):
    """The CLI for this task"""
    retrieve_legislation(metadata_files, output_path)

if __name__ == "__main__":
    typer.run(main)
