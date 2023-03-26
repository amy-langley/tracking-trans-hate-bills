from typing import Dict

from nltk import ngrams, FreqDist
import typer

from lib.util import load_json, write_json

def generate_ngrams(
    tokens_path: str,
    ngram_length: int,
    min_occurrences: int = 20,
) -> Dict[str, int]:
    """Get all ngrams of specified length and at least min freq"""
    all_tokens = load_json(tokens_path)
    raw_ngrams = ngrams(all_tokens, ngram_length)
    dist = FreqDist(raw_ngrams)
    return {
        ' '.join(k): v
        for k, v
        in dist.items()
        if v > min_occurrences
    }

def main(
    tokens_path: str,
    ngrams_path: str,
    ngram_length: int = typer.Option(10),
    min_occurrences: int = typer.Option(20),
):
    """The CLI for this task"""
    frequent_ngrams = generate_ngrams(tokens_path, ngram_length, min_occurrences)
    write_json(frequent_ngrams, ngrams_path)

if __name__ == "__main__":
    typer.run(main)
