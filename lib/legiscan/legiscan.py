from itertools import chain
import json
import logging
from mergedeep import merge
from operator import itemgetter
import pandas as pd
import re
import typer
from typing import Dict, Iterable, Set, Tuple

from lib.legiscan import locate_matches
from lib.util import load_json

app = typer.Typer()
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
        with open(resolver_map, 'r') as f:
            mapper = json.load(f)
    except Exception as e:
        logger.warning(f'Failed to load mapper: {e}')
        mapper = {}

    hints = {}
    try:
        with open(hint_map, 'r') as f:
            hints = json.load(f)
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

    with open(resolver_map, 'w') as f:
        json.dump(mapper, f, indent=2)

    # after generating and saving inferred map, merge in explicit hints before continuing
    hinted = {}
    merge(hinted, mapper, hints)
    return hinted

def match_is_relevant(state: str, bill_id: str, match: Dict, strict: bool=True) -> bool:
    if match['state'] != state:
        return False
    
    if match['relevance'] < 50:
        return False
    
    bill_number = match['bill_number']
    searched_prefix = re.sub(r'[^A-Z]+$', '', bill_id)
    proposed_prefix = re.sub(r'[^A-Z]+$', '', bill_number)
    
    if strict:
        if not searched_prefix == proposed_prefix:
            return False
    else:
        if searched_prefix[0] != proposed_prefix[0]:
            return False
        
    searched_digits = re.sub(r'^\D+0*', '', bill_id)
    proposed_digits = re.sub(r'^\D+0*', '', bill_number)

    if not searched_digits == proposed_digits:
        return False

    return True

def attempt_resolve_one(mapper, state: str, bill_id: str):
    if state not in mapper:
        raise ValueError(f'Unknown state {state} for {state} {bill_id}')
    
    bill_id = bill_id.replace('23-', '')
    
    state_record = mapper[state]
    if 'bills' not in state_record:
        state_record['bills'] = {}

    state_known_bills = state_record['bills'].keys()

    if bill_id in state_known_bills:
        # print(f'Matching {state} {bill_id} with known lsid {state_record["bills"][bill_id]}')
        return
    
    prefixes, zfill = itemgetter('prefixes', 'zfill')(state_record['meta'])
    candidate_prefixes = [prefix for prefix in prefixes if prefix.startswith(bill_id[0])]
    if len(candidate_prefixes) < 1:
        raise ValueError(f'Unknown prefix {bill_id[0]} for {state} {bill_id}')
    
    bill_digits = re.sub(r'^\D+', '', bill_id)

    candidate_names = [f'{prefix}{bill_digits.zfill(zfill)}' for prefix in candidate_prefixes]
    synonyms = [bill for bill in state_known_bills if bill in candidate_names]
    
    if len(synonyms) == 1:
        # print(f'Matching {state} {bill_id} with known lsid {state_record["bills"][synonyms[0]]}')
        return None
    elif len(synonyms) > 1:
        raise ValueError(f'Multiple candidate synonyms {synonyms} for {state} {bill_id}')
    
    strict_matches = chain.from_iterable(locate_matches(state, candidate_name) for candidate_name in candidate_names)

    # make increasingly far-fetched attempts to find a unique relevant match
    relevant_matches = [match for match in strict_matches if match_is_relevant(state, bill_id, match)]
    
    if len(relevant_matches) == 0:
        relevant_matches = [match for match in strict_matches if match_is_relevant(state, bill_id, match, strict=False)]
    
    loose_matches = []
    if len(relevant_matches) == 0:
        loose_matches = list(locate_matches(state, bill_digits))
        # no nice lookup, time to try a hail mary
        relevant_matches = [match for match in loose_matches if match_is_relevant(state, bill_id, match)]
    
    if len(relevant_matches) == 0:
        relevant_matches = [match for match in loose_matches if match_is_relevant(state, bill_id, match, strict=False)]
        
    # no more tricks up my sleeve
    if len(relevant_matches) == 0:
        raise ValueError(f'No relevant matches for {state} {bill_id}')
    
    if len(relevant_matches) == 1:
        match = relevant_matches[0]
        print(f'Matching {state} {bill_id} with lsid {match["bill_id"]} {match["state"]} {match["bill_number"]} ({match["title"]})')
        return match
    
    if len(relevant_matches) > 1:
        match_ids = [match['bill_id'] for match in relevant_matches]
        raise ValueError(f'Multiple relevant matches for {state} {bill_id}: {match_ids}')

def augment_resolver_map(mapper, new_bills: Tuple[str, str], output_path):
    mapped = 0
    total_bills = len(new_bills)
    for new_bill in new_bills:
        try:
            match = attempt_resolve_one(mapper, *new_bill)
            mapped = mapped + 1
            if match:
                state, bill_number, bill_id = itemgetter('state', 'bill_number', 'bill_id')(match)
                if 'bills' not in mapper[state]:
                    mapper[state]['bills'] = {}
                    
                mapper[state]['bills'][bill_number] = bill_id
        except Exception as e:
            print(f'Error: {new_bill} {e}')

    print(f'Successfully mapped {mapped}/{total_bills} bills ({total_bills-mapped} not mapped)')
    with open(output_path, 'w') as f:
        json.dump(mapper, f, indent=2)
    print('Changes persisted')
        

@app.command('infer-resolver-map')
def cli_infer_resolver_map(
    ttl_dataset_path: str,
    resolver_hint_path: str,
    resolver_map_path: str,
):
    result = infer_resolver_map(ttl_dataset_path, resolver_map_path, resolver_hint_path)
    logger.info(f'Finished inferring structure')

    
@app.command('augment-resolver-map')
def cli_augment_resolver_map(
    resolver_map_path: str,
    data_set_path: str,
    output_path: str,
):
    resolver_map = load_json(resolver_map_path)
    new_data = pd.read_json(data_set_path)
    tuples = [(row['state']['value'], row['name']) for idx, row in new_data.iterrows()]
    augment_resolver_map(
        resolver_map,
        tuples,
        output_path,
    )

if __name__ == "__main__":
    app()
