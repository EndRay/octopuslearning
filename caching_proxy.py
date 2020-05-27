from functools import lru_cache

from flask import Flask, request
from requests import get

app = Flask('__main__')
SITE_NAME = 'https://codeforces.com/'

@lru_cache(maxsize=None)
def get_data(url):
  return get(url).content

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
  params = '&'.join([f'{k}={v}' for k, v in request.args.items()])
  return get_data(f'{SITE_NAME}{path}?{params}')

app.run(host='0.0.0.0', port=8080)