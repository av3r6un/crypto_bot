import time
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
from config import Config as cfg

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'


def request(slug, currency):
    data = None
    parameters = {
        'slug': slug,
        'convert': currency
    }
    headers = {
      'Accepts': 'application/json',
      'X-CMC_PRO_API_KEY': cfg.CMC_API
    }
    session = Session()
    session.headers.update(headers)
    try:
        r = session.get(url, params=parameters)
        data = json.loads(r.text)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
    return data