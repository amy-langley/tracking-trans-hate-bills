from itertools import chain
from typing import Dict, List, Set, Tuple

import typer

from lib.util import load_json, write_json

def categorize_record(record: Dict, keywords: List[Tuple[str, str]]) -> Set[str]:
    """Given a record and a list of keywords, try to categorize it"""
    return set(
        keyword[0]
        for keyword
        in keywords
        if (
            keyword[1] in record['title'].lower()
            or
            keyword[1] in record['description'].lower()
        )
    )

def categorize_aggregate_dataset(
    categories_definition_path: str,
    aggregate_data_path: str,
    output_path: str,
):
    """Given a list of categories and keywords try to categorize aggregate dataset"""
    categories = load_json(categories_definition_path)
    aggregates = load_json(aggregate_data_path)

    keywords: List[Tuple[str, str]] = list(chain.from_iterable(
        ((category['name'], keyword) for keyword in category['keywords'])
        for category
        in categories
    ))

    categorized = list(
        (
            aggregate['state'],
            aggregate['bill_id'],
            categorize_record(aggregate, keywords)
        )

        for aggregate
        in aggregates
    )

    grouped = {
        category['name']: [
            categorize[0:2]
            for categorize
            in categorized
            if category['name'] in categorize[2]
        ]
        for category
        in categories
    }

    grouped['Uncategorized'] = [
        categorize[0:2]
        for categorize
        in categorized
        if len(categorize[2]) == 0
    ]

    write_json(grouped, output_path)

    return grouped

def main(
    categories_definition_path: str,
    aggregate_data_path: str,
    output_path: str,
):
    """The CLI for this task"""
    categorize_aggregate_dataset(
        categories_definition_path,
        aggregate_data_path,
        output_path,
    )

if __name__ == "__main__":
    typer.run(main)
