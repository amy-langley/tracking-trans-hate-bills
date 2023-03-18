import base64
from bs4 import BeautifulSoup as Soup
import json
import logging
import os
import requests_cache

from .types import BillDescriptor


logger = logging.getLogger(__name__)


def get_bill_meta_filename(descriptor: BillDescriptor, path: str):
    return f'{path}/bill_meta_{descriptor.state}_{descriptor.bill_id}.json'


def get_bill_text_response_filename(descriptor: BillDescriptor, path: str):
    return f'{path}/bill_text_response_{descriptor.state}_{descriptor.bill_id}.json'


def get_bill_contents_filename(descriptor: BillDescriptor, path, extension):
    return f'{path}/{descriptor.state}_{descriptor.bill_id}.{extension}'


def make_legiscan_session():
    FORM_URL = 'https://legiscan.com/user/login'
    CREDENTIAL_DATA = {
        'name': os.environ["LEGISCAN_USERNAME"],
        'pass': os.environ["LEGISCAN_PASSWORD"],
    }

    session = requests_cache.CachedSession('legiscan', cache_control=True, use_temp=True)
    get_form = session.get(FORM_URL)
    soup = Soup(get_form.content, features="html.parser")

    login_form = soup.find(id='user-login')
    form_build_id = login_form.find('input', {'name': 'form_build_id'}).get('value')
    form_id = login_form.find('input', {'name': 'form_id'}).get('value')
    op = login_form.find('input', {'name': 'op'}).get('value')

    post_data = {
        **CREDENTIAL_DATA,
        'form_build_id': form_build_id,
        'form_id': form_id,
        'op': op,
    }

    session.post(FORM_URL, data=post_data)
    return session


def extract_bill_contents(descriptor: BillDescriptor, path: str, response_path: str):
    result = None
    
    if not response_path:
        logger.warning(f'Missing response data {get_bill_text_response_filename(descriptor, path)}')
        return None
    
    with open(response_path, 'r') as f:
        result = json.load(f)['text']

    doc = result['doc']
    extension = result['mime'].split('/')[-1]
    local_filename = get_bill_contents_filename(descriptor, path, extension)

    with open(local_filename, 'wb') as f:
        f.write(base64.b64decode(doc))
    
    logger.debug(f'Extracted {local_filename}')
    return local_filename
