from glob import glob
from itertools import chain
import logging

from lib.language import canonicalize_tokens, clean_text, clean_tokens, tokenize_text
from lib.language.types import TokenStream
from lib.util import chain as chain_calls, extract_text


logger = logging.getLogger(__name__)


def tokenize_corpus(globby_path: str) -> TokenStream:
    """Convert a directory full of files into a stream of lemmatized tokens"""
    return chain.from_iterable(
        chain_calls(
            extract_text,
            clean_text,
            tokenize_text,
            clean_tokens,
            list,  # must force eager evaluation here for lemmatizing
            canonicalize_tokens,
        )(bill)
        for bill
        in glob(globby_path)
    )
