from functools import reduce
from itertools import chain

from nltk import FreqDist
import typer

from lib.util import load_json, write_json

def est_phrase_probability(phrase, probs):
    """Estimate probability of a given phrase"""
    return reduce(
        lambda x, y: x * probs[y],
        phrase.split(' '),
        1
    )

def calculate_ngram_likelihood(
    ngrams_path: str,
    bill_tokens_path: str,
    neutral_tokens_path: str,
):
    """Calculate the likelihood of ngrams in corpus"""
    ngrams = load_json(ngrams_path)
    raw_tokens = chain(
        load_json(bill_tokens_path),
        load_json(neutral_tokens_path),
    )

    dist = FreqDist(raw_tokens)
    token_count = reduce(lambda x, y: x+y, dist.values(), 0)

    probabilities = {
        k: v/token_count
        for k, v
        in dist.items()
    }

    return sorted([
            [
                phrase,
                occurrences,
                est_phrase_probability(phrase, probabilities)
            ]
            for phrase, occurrences
            in ngrams.items()
        ],
        key = lambda n: n[1],
    )

def main(
    ngrams_path: str,
    bill_tokens_path: str,
    neutral_tokens_path: str,
    output_path: str,
):
    """The CLI for this task"""
    ngram_probs = calculate_ngram_likelihood(
        ngrams_path,
        bill_tokens_path,
        neutral_tokens_path,
    )

    write_json(ngram_probs, output_path)

if __name__ == "__main__":
    typer.run(main)
