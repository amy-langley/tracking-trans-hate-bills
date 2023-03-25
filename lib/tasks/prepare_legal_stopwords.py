from typing import List

from nltk import FreqDist
import typer

from lib.util import load_json, write_json

def prepare_legal_stopwords(
    token_path: str,
    output_filename: str,
    min_frequency: int=800
) -> List[str]:
    """Get the most frequent terms from the neutral legal corpus"""
    canonicalized_tokens = load_json(token_path)

    distribution = FreqDist(canonicalized_tokens)

    stopwords = list(
        k
        for k, v
        in distribution.items()
        if v > min_frequency and len(k) > 1
    )

    write_json(stopwords, output_filename)

    return stopwords

def main(
    token_path: str,
    output_filename: str,
    min_frequency: int = typer.Option(800)
):
    """The CLI for this task"""
    prepare_legal_stopwords(token_path, output_filename, min_frequency)

if __name__ == "__main__":
    typer.run(main)
