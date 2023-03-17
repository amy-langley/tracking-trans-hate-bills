import base64
from bs4 import BeautifulSoup as Soup
import json
import os
import requests_cache

def get_bill_meta_filename(state, bill_id):
    return f'../tmp/legiscan/bill_meta_{state}_{bill_id}.json'

def get_bill_text_response_filename(state, bill_id):
    return f'../tmp/legiscan/bill_text_response_{state}_{bill_id}.json'

def get_bill_contents_filename(state, bill_id, extension):
    return f'../bills/{state}_{bill_id}.{extension}'

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


def extract_bill_contents(state, bill_id, legiscan_bill_id, _meta_path, response_path: str):
    result = None
    
    if not response_path:
        print(f'Missing response data {get_bill_text_response_filename(state, bill_id)}')
        return None
    
    with open(response_path, 'r') as f:
        result = json.load(f)['text']

    doc = result['doc']
    extension = result['mime'].split('/')[-1]
    local_filename = get_bill_contents_filename(state, bill_id, extension)

    with open(local_filename, 'wb') as f:
        f.write(base64.b64decode(doc))
    
    #print(f'Created {local_filename}')
    return local_filename
