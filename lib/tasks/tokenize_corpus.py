from glob import glob
from itertools import chain
import logging
import os.path

from lib.language import canonicalize_tokens, clean_text, clean_tokens, tokenize_text
from lib.language.types import TokenStream
from lib.util import chain as chain_calls, extract_html_text, extract_pdf_text


logger = logging.getLogger(__name__)


def extract_text(file_path: str) -> str:
    try:
        if file_path.endswith('.html'):
            return extract_html_text(file_path)

        if file_path.endswith('.pdf'):
            return extract_pdf_text(file_path)

        raise ValueError(f'Unknown file type {file_path}')
    except Exception as e:
        logger.warning(f'Failed to extract {file_path}: {e}')
        return ''


def tokenize_corpus(globby_path: str) -> TokenStream:
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
