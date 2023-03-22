import logging

from typing import Optional

from .html import extract_html_text
from .pdf import extract_pdf_text


logger = logging.getLogger(__name__)


def extract_text(file_path: str) -> Optional[str]:
    """Extract text from any kind of file as long as it's html or pdf"""
    try:
        if file_path.endswith('.html'):
            return extract_html_text(file_path)

        if file_path.endswith('.pdf'):
            return extract_pdf_text(file_path)

        raise ValueError(f'Unknown file type {file_path}')
    except Exception as an_exception:  # pylint: disable=W0718
        logger.warning(f'Failed to extract {file_path}: {an_exception}')
        return None
