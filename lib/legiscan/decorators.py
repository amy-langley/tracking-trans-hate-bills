from functools import wraps
import os
import requests_cache

from .util import make_legiscan_session


def legiscan_auth(authorized_action):
    """Use this decorator for authorized access to the legiscan web app"""
    @wraps(authorized_action)
    def authorization_wrapper(*args, **kwargs):
        if 'session' in kwargs:
            return authorized_action(*args, **kwargs)

        with make_legiscan_session() as session:
            new_kwargs = kwargs | { 'session': session }
            return authorized_action(*args, **new_kwargs)

    return authorization_wrapper


def legiscan_api(api_action):
    """Use this decorator for authorized access to the legiscan api"""
    api_key = os.environ.get("LEGISCAN_API_KEY")
    session = requests_cache.CachedSession('legiscan', cache_control=True, use_temp=True)

    injected_kwargs = {}

    @wraps(api_action)
    def api_wrapper(*args, **kwargs):
        if 'api_key' not in kwargs or not kwargs['api_key']:
            injected_kwargs['api_key'] = api_key

        if 'session' not in kwargs or not kwargs['session']:
            injected_kwargs['session'] = session

        return api_action(*args, **(kwargs | injected_kwargs))

    return api_wrapper
