import base64
import logging
import os
import requests_cache

from bs4 import BeautifulSoup as Soup
from lib.util import load_json

from .types import BillDescriptor


logger = logging.getLogger(__name__)


def get_bill_meta_filename(descriptor: BillDescriptor, path: str):
    """Generate a standardized metadata filename"""
    return f'{path}/bill_meta_{descriptor.state}_{descriptor.bill_id}.json'


def get_bill_text_response_filename(descriptor: BillDescriptor, path: str):
    """Generate a standardized text response filename"""
    return f'{path}/bill_text_response_{descriptor.state}_{descriptor.bill_id}.json'


def get_bill_contents_filename(descriptor: BillDescriptor, path, extension):
    """Generate an output filename for bill contents"""
    return f'{path}/{descriptor.state}_{descriptor.bill_id}.{extension}'


def make_legiscan_session():
    """Get a logged-in request session for the legiscan web app"""
    form_url = 'https://legiscan.com/user/login'
    credential_data = {
        'name': os.environ["LEGISCAN_USERNAME"],
        'pass': os.environ["LEGISCAN_PASSWORD"],
    }

    session = requests_cache.CachedSession('legiscan', cache_control=True, use_temp=True)
    get_form = session.get(form_url)
    soup = Soup(get_form.content, features="html.parser")

    login_form = soup.find(id='user-login')
    form_build_id = login_form.find('input', {'name': 'form_build_id'}).get('value')
    form_id = login_form.find('input', {'name': 'form_id'}).get('value')
    operation = login_form.find('input', {'name': 'op'}).get('value')

    post_data = {
        **credential_data,
        'form_build_id': form_build_id,
        'form_id': form_id,
        'op': operation,
    }

    session.post(form_url, data=post_data)
    return session


def extract_bill_contents(descriptor: BillDescriptor, path: str, response_path: str):
    """Get the real document out of the base64 encoded response"""
    result = None

    if not response_path:
        logger.warning(f'Missing response data {get_bill_text_response_filename(descriptor, path)}')
        return None

    result = load_json(response_path)['text']

    doc = result['doc']
    extension = result['mime'].split('/')[-1]
    local_filename = get_bill_contents_filename(descriptor, path, extension)

    with open(local_filename, 'wb') as destination:
        destination.write(base64.b64decode(doc))

    logger.debug(f'Extracted {local_filename}')
    return local_filename
