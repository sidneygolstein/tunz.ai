# helpers.py
# Allow to detect if we are on host url or deployed on cloud. 

from flask import request, url_for

def get_scheme():
    if request.host.startswith('127.0.0.1') or request.host.startswith('localhost'):
        return 'http'
    else:
        return 'https'

def get_url(endpoint, **values):
    scheme = get_scheme()
    return url_for(endpoint, _external=True, _scheme=scheme, **values)