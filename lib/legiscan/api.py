import os
import json
import logging
from typing import Iterable, Dict, Optional

from lib.util import load_json

from .decorators import legiscan_api
from .types import BillDescriptor
from .util import get_bill_meta_filename, get_bill_text_response_filename


logger = logging.getLogger(__name__)
LEGISCAN_API_URL = 'https://api.legiscan.com/'


@legiscan_api
def get_bill_meta(descriptor: BillDescriptor, path: str, api_key: str, session) -> Optional[str]:
    """Get metadata from legiscan for a bill"""
    local_filename = get_bill_meta_filename(descriptor, path)

    if os.path.exists(local_filename):
        logger.debug(f'Using existing local {local_filename}')
        return local_filename

    assembled_params = {
        'key': api_key,
        'op': 'getBill',
        'id': descriptor.legiscan_bill_id,
    }
    resp = session.get(LEGISCAN_API_URL, params=assembled_params)

    if not resp.ok:
        logger.warning(f'Error {resp.status_code} downloading {local_filename}')
        return None

    parsed = json.loads(resp.text)
    if parsed['status'].upper() == 'ERROR':
        logger.warning(f'Error {parsed["alert"]["message"]} downloading {local_filename}')
        return None

    with open(local_filename, 'wb') as destination:
        destination.write(resp.content)

    logger.debug(f'Retrieved metadata file {local_filename}')
    return local_filename


@legiscan_api
def get_bill_text(
    descriptor: BillDescriptor,
    path: str,
    bill_meta_path: str,
    api_key: str,
    session
) -> Optional[str]:
    """Get the contents of a bill, discovering the doc id from metadata"""
    local_filename = get_bill_text_response_filename(descriptor, path)

    if not bill_meta_path:
        logger.info(f'Missing meta data {get_bill_meta_filename(descriptor, path)}')
        return None

    meta = load_json(bill_meta_path)

    texts = meta['bill']['texts']
    sorted_texts = sorted(texts, key=lambda x: x['date'], reverse=True)

    if len(sorted_texts) < 1:
        logger.info(f'No bill texts available yet for {bill_meta_path}')
        return None

    doc_id = sorted_texts[0]['doc_id']

    if os.path.exists(local_filename):
        logger.debug(f'Using existing local {local_filename}')
        return local_filename

    assembled_url = f'https://api.legiscan.com/?key={api_key}&op=getBillText&id={doc_id}'
    resp = session.get(assembled_url)

    if not resp.ok:
        logger.warning(f'Error {resp.status_code} downloading {local_filename}')
        return None

    parsed = json.loads(resp.text)
    if parsed['status'].upper() == 'ERROR':
        logger.warning(f'Error {parsed["alert"]["message"]} downloading {local_filename}')
        return None

    with open(local_filename, 'wb') as source:
        source.write(resp.content)

    logger.debug(f'Retrieved bill text response {local_filename}')
    return local_filename


# TODO: this is a clumsy way to handle this
@legiscan_api
def get_bill_text_direct(
    descriptor: BillDescriptor,
    path: str,
    doc_id: str,
    api_key: str,
    session
) -> Optional[str]:
    """Get the contents of a bill with an already-known doc id"""
    local_filename = get_bill_text_response_filename(descriptor, path)

    if os.path.exists(local_filename):
        logger.debug(f'Using existing local {local_filename}')
        return local_filename

    assembled_params = {
        'key': api_key,
        'op': 'getBillText',
        'id': doc_id,
    }
    resp = session.get(LEGISCAN_API_URL, params=assembled_params)

    if not resp.ok:
        logger.warning(f'Error {resp.status_code} downloading {local_filename}')
        return None

    parsed = json.loads(resp.text)
    if parsed['status'].upper() == 'ERROR':
        logger.warning(f'Error {parsed["alert"]["message"]} downloading {local_filename}')
        return None

    with open(local_filename, 'wb') as destination:
        destination.write(resp.content)

    logger.debug(f'Retrieved bill text response {local_filename}')
    return local_filename


@legiscan_api
def locate_matches(state: str, candidate_name: str, api_key: str, session) -> Iterable[Dict]:
    """Attempt to locate a matching bill in legiscan"""
    assemble_params = {
        'key': api_key,
        'op': 'getSearch',
        'state': state,
        'query': candidate_name,
    }
    search_result = json.loads(
        session.get(LEGISCAN_API_URL, params=assemble_params).text
    )['searchresult']
    result_count = search_result['summary']['count']
    return (search_result[str(idx)] for idx in range(min(result_count, 50)))
