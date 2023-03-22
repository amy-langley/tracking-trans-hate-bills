import logging
import re

from itertools import chain
from operator import itemgetter
from typing import Dict, List, Tuple

import pandas as pd
import typer

from lib.legiscan import locate_matches
from lib.util import load_json, write_json

logger = logging.getLogger(__name__)

def match_is_relevant(state: str, bill_id: str, match: Dict, strict: bool=True) -> bool:
    """Given a candidate match, evaluate if we should accept it"""
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
    """Try to figure out the legiscan id for one bill"""
    if state not in mapper:
        raise ValueError(f'Unknown state {state} for {state} {bill_id}')

    # i'm not sure why CO does things like HB 23-1234 but it sucks
    bill_id = bill_id.replace('23-', '')

    state_record = mapper[state]
    if 'bills' not in state_record:
        state_record['bills'] = {}

    state_known_bills = state_record['bills'].keys()

    if bill_id in state_known_bills:
        logger.debug(
            f'Matching {state} {bill_id} with known lsid {state_record["bills"][bill_id]}'
        )
        return

    prefixes, zfill = itemgetter('prefixes', 'zfill')(state_record['meta'])
    candidate_prefixes = [prefix for prefix in prefixes if prefix.startswith(bill_id[0])]
    if len(candidate_prefixes) < 1:
        raise ValueError(f'Unknown prefix {bill_id[0]} for {state} {bill_id}')

    bill_digits = re.sub(r'^\D+', '', bill_id)

    candidate_names = [f'{prefix}{bill_digits.zfill(zfill)}' for prefix in candidate_prefixes]
    synonyms = [bill for bill in state_known_bills if bill in candidate_names]

    if len(synonyms) == 1:
        logger.debug(
            f'Matching {state} {bill_id} with known lsid {state_record["bills"][synonyms[0]]}'
        )
        return None

    if len(synonyms) > 1:
        raise ValueError(f'Multiple candidate synonyms {synonyms} for {state} {bill_id}')

    strict_matches = chain.from_iterable(
        locate_matches(state, candidate_name) # pylint: disable=E1120
        for candidate_name
        in candidate_names
    )

    # make increasingly far-fetched attempts to find a unique relevant match
    relevant_matches = [
        match
        for match
        in strict_matches
        if match_is_relevant(state, bill_id, match)
    ]

    if len(relevant_matches) == 0:
        relevant_matches = [
            match
            for match
            in strict_matches
            if match_is_relevant(state, bill_id, match, strict=False)
        ]

    loose_matches = []
    if len(relevant_matches) == 0:
        loose_matches = list(locate_matches(state, bill_digits)) # pylint: disable=E1120
        # no nice lookup, time to try a hail mary
        relevant_matches = [
            match
            for match
            in loose_matches
            if match_is_relevant(state, bill_id, match)
        ]

    if len(relevant_matches) == 0:
        relevant_matches = [
            match
            for match
            in loose_matches
            if match_is_relevant(state, bill_id, match, strict=False)
        ]

    # no more tricks up my sleeve
    if len(relevant_matches) == 0:
        raise ValueError(f'No relevant matches for {state} {bill_id}')

    if len(relevant_matches) == 1:
        match = relevant_matches[0]
        logger.info(
            f'Matching {state} {bill_id} with lsid {match["bill_id"]}'
            f' {match["state"]} {match["bill_number"]} ({match["title"]})'
        )
        return match

    if len(relevant_matches) > 1:
        match_ids = [match['bill_id'] for match in relevant_matches]
        raise ValueError(f'Multiple relevant matches for {state} {bill_id}: {match_ids}')

def augment_resolver_map(mapper, new_bills: List[Tuple[str, str]], output_path):
    """Given a resolver map and a list of new bills to locate, try to resolve them"""
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
        except Exception as an_exception:  # pylint: disable=W0718
            logger.warning(f'Resolution failure: {new_bill} {an_exception}')

    logger.info(
        f'Successfully mapped {mapped}/{total_bills} bills ({total_bills-mapped} not mapped)'
    )
    write_json(mapper, output_path)


def main(
    resolver_map_path: str,
    data_set_path: str,
    output_path: str,
):
    """The cli for this task"""
    resolver_map = load_json(resolver_map_path)
    new_data = pd.read_json(data_set_path)

    tuples = [
        (row['state']['value'], row['name'])
        for _, row
        in new_data.iterrows()  # pylint: disable=E1101 # shut up yes it does
    ]

    augment_resolver_map(
        resolver_map,
        tuples,
        output_path,
    )

if __name__ == "__main__":
    typer.run(main)
