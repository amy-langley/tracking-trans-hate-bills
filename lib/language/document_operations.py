from nltk import word_tokenize as tokenize_text

from lib.util import extract_text, chain as chain_calls

from .text_operations import clean_text
from .token_operations import canonicalize_tokens, clean_tokens
from .types import TokenStream

def tokenize_file(file_path: str) -> TokenStream:
    """Given a path, return a stream of canonicalized tokens"""
    return chain_calls(
        extract_text,
        clean_text,
        tokenize_text,
        clean_tokens,
        list,  # must force eager evaluation here for lemmatizing
        canonicalize_tokens,
    )(file_path)
