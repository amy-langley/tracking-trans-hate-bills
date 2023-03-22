import logging
from mergedeep import merge
import pandas as pd
import re
import typer
from typing import Iterable, Set

from lib.util import load_json, write_json

logger = logging.getLogger(__name__)

def infer_prefixes(bill_ids: Iterable[str]) -> Set[str]:
    return set(
        re.sub(r'(\d|\s)+$', '', bill_id)
        for bill_id
        in bill_ids
    )

def infer_zfill(bill_ids: Iterable[str]) -> int:
    digits = [len(re.sub(r'^\D+', '', bill_id)) for bill_id in bill_ids]
    return min([100, *digits])

def infer_resolver_map(
    ttl_data_path: str, 
    resolver_map: str,
    hint_map: str,
):
    mapper = {}
    try:
        mapper = load_json(resolver_map)
    except Exception as e:
        logger.warning(f'Failed to load mapper: {e}')
        mapper = {}

    hints = {}
    try:
        hints = load_json(hint_map)
    except Exception as e:
        logger.warning(f'Failed to load hints: {e}')
        hints = {}

    ttl_data = pd.read_json(ttl_data_path)
    
    for state, group in ttl_data.groupby(by='state'):
        state_map = mapper[state] if state in mapper else {}

        existing_bills_map = state_map['bills'] if 'bills' in state_map else {}
        observed_bills_map = {
            row['billId']: row['legiscanId']
            for idx, row in group.iterrows()
        }
        
        state_map['bills'] = {
            **observed_bills_map,
            **existing_bills_map,
        }
        
        existing_meta = state_map['meta'] if 'meta' in state_map else {}
        observed_meta = {
            'prefixes': list(infer_prefixes(state_map['bills'].keys())),
            'zfill': infer_zfill(state_map['bills'].keys()),
        }

        state_map['meta'] = {
            **observed_meta,
            **existing_meta,
        }
        
        mapper[state] = state_map

    write_json(mapper, resolver_map)

    # after generating and saving inferred map, merge in explicit hints before continuing
    hinted = {}
    merge(hinted, mapper, hints)
    return hinted

def main(
    ttl_dataset_path: str,
    resolver_hint_path: str,
    resolver_map_path: str,
):
    result = infer_resolver_map(ttl_dataset_path, resolver_map_path, resolver_hint_path)
    logger.info(f'Finished inferring structure')
    
if __name__ == "__main__":
    typer.run(main)
