import os
import json
from typing import Iterable, Dict

from .decorators import legiscan_api
from .util import get_bill_meta_filename, get_bill_text_response_filename


@legiscan_api
def get_bill_meta(state, bill_id, legiscan_bill_id, api_key: str, session) -> str:
    local_filename = get_bill_meta_filename(state, bill_id)

    if os.path.exists(local_filename):
        #print(f'skipping {local_filename}, exists')
        return local_filename

    assembled_url = f'https://api.legiscan.com/?key={api_key}&op=getBill&id={legiscan_bill_id}'
    resp = session.get(assembled_url)

    if not resp.ok:
        print(f'Error {resp.status_code} downloading {local_filename}')
        return None
    
    parsed = json.loads(resp.text)
    if parsed['status'].upper() == 'ERROR':
        print(f'Error {parsed["alert"]["message"]} downloading {local_filename}')
        return None
    
    with open(local_filename, 'wb') as f:
        f.write(resp.content)
    
    print(f'got {local_filename}')
    return local_filename


@legiscan_api
def get_bill_text(state, bill_id, legiscan_bill_id, bill_meta_path: str, api_key: str, session) -> str:
    local_filename = get_bill_text_response_filename(state, bill_id)

    if not bill_meta_path:
        print(f'Missing meta data {get_bill_meta_filename(state, bill_id)}')
        return None

    meta = None
    with open(bill_meta_path, 'r') as f:
        meta = json.load(f)

    texts = meta['bill']['texts']
    sorted_texts = sorted(texts, key=lambda x: x['date'], reverse=True)
    
    if len(sorted_texts) < 1:
        print(f'No bill texts available yet for {bill_meta_path}')
        return None
    
    doc_id = sorted_texts[0]['doc_id']

    if os.path.exists(local_filename):
        # print(f'skipping {local_filename}, exists')
        return local_filename

    assembled_url = f'https://api.legiscan.com/?key={api_key}&op=getBillText&id={doc_id}'
    resp = session.get(assembled_url)

    if not resp.ok:
        print(f'Error {resp.status_code} downloading {local_filename}')
        return None
    
    parsed = json.loads(resp.text)
    if parsed['status'].upper() == 'ERROR':
        print(f'Error {parsed["alert"]["message"]} downloading {local_filename}')
        return None
    
    with open(local_filename, 'wb') as f:
        f.write(resp.content)
    
    print(f'got {local_filename}')
    return local_filename


@legiscan_api
def locate_matches(state: str, candidate_name: str, api_key: str, session) -> Iterable[Dict]:
    assemble_params = {
        'key': api_key,
        'op': 'getSearch',
        'state': state,
        'query': candidate_name,
    }
    search_result = json.loads(session.get(LEGISCAN_API_URL, params=assemble_params).text)['searchresult']
    result_count = search_result['summary']['count']
    return (search_result[str(idx)] for idx in range(min(result_count, 50)))
