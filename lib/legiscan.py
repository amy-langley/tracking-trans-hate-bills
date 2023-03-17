from bs4 import BeautifulSoup as Soup
from datetime import timedelta
from functools import wraps
import os
import requests_cache
from typing import Optional

def make_legiscan_session():
    FORM_URL = 'https://legiscan.com/user/login'
    CREDENTIAL_DATA = {
        'name': os.environ.get("LEGISCAN_USERNAME"),
        'pass': os.environ.get("LEGISCAN_PASSWORD"),
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
    LEGISCAN_SESSION = session
    return session

def legiscan_auth(authorized_action):
    @wraps(authorized_action)
    def authorization_wrapper(*args, **kwargs):
        if 'session' in kwargs:
            return authorized_action(*args, **kwargs)
        
        with make_legiscan_session() as session:
            new_kwargs = kwargs | { 'session': session }
            return authorized_action(*args, **new_kwargs)
    
    return authorization_wrapper

def legiscan_api(api_action):
    API_KEY = os.environ.get("LEGISCAN_API_KEY")
    session = requests_cache.CachedSession('legiscan', cache_control=True, use_temp=True)

    injected_kwargs = {}
    
    @wraps(api_action)
    def api_wrapper(*args, **kwargs):
        if 'api_key' not in kwargs or not kwargs['api_key']:
            injected_kwargs['api_key'] = API_KEY
        
        if 'session' not in kwargs or not kwargs['session']:
            injected_kwargs['session'] = session
        
        return api_action(*args, **(kwargs | injected_kwargs))
                          
    return api_wrapper
