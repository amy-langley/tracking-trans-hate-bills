import logging
import time

from itertools import chain
from typing import List

import typer

from lib.legiscan import BillDescriptor, get_bill_meta
from lib.util import load_json


logger = logging.getLogger(__name__)


def retrieve_legiscan_metadata(
    resolver_map_path: str,
    output_path: str,
) -> List[str]:
    """Download the metadata for all the bills in resolver map"""
    resolver_map = load_json(resolver_map_path)
    tuples = chain.from_iterable(
        (BillDescriptor(state, k, v) for k, v in m['bills'].items())
        for state, m
        in resolver_map.items()
    )

    return [
        get_bill_meta(tuple, output_path)  # pylint: disable=E1120
        for tuple
        in tuples
    ]


def main(
    resolver_map_path: str,
    output_path: str,
):
    """The CLI for this task"""
    start = time.time()
    result = retrieve_legiscan_metadata(resolver_map_path, output_path)
    end = time.time()
    logger.info(
        f'Retrieved {len(result)} items in {end-start:.2f}'
    )


if __name__ == "__main__":
    typer.run(main)
