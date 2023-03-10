from bs4 import BeautifulSoup as Soup
from functools import wraps
import os
import requests
from typing import Optional

def legiscan_auth(authorized_action):
    FORM_URL = 'https://legiscan.com/user/login'
    CREDENTIAL_DATA = {
        'name': os.environ.get("LEGISCAN_USERNAME"),
        'pass': os.environ.get("LEGISCAN_PASSWORD"),
    }

    def make_legiscan_session() -> requests.Session:
        session = requests.Session()
        get_form = session.get(FORM_URL)
        soup = Soup(get_form.content, features="html5lib")

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
    
    @wraps(authorized_action)
    def authorization_wrapper(*args, **kwargs):
        if 'session' in kwargs:
            return authorized_action(*args, **kwargs)
        
        with make_legiscan_session() as session:
            new_kwargs = kwargs | { 'session': session }
            return authorized_action(*args, **new_kwargs)
    
    return authorization_wrapper
