import json
import time
import schedule
from datetime import datetime
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from config import Config as cfg

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

dbData = {
    'id': '1',
    'user_id': 1039572834,
    'username': 'Alexandr',
    'tokens': 'cardano, eos, theta',
    'currency': 'usd',
    'period': 2,
    'start_time': '19:36:52'
},{
    'id': '2',
    'user_id': 1039572836,
    'username': 'Alexandro',
    'tokens': 'bitcoin, ethereum',
    'currency': 'usd',
    'period': 3,
    'start_time': '19:36:59'
}


def request_data():
    with open('data/data.json', 'r') as file:
        cryptoData = json.load(file)
    return cryptoData


def ts():
    timestamp = datetime.now().strftime("%H:%M:%S")
    return timestamp


def message(slug, curr):
    a = request(slug, curr)
    prettify(a)


def prettify(a):
    answer_list = []
    for el in a['data'].items():
        symbol = el[1]['symbol']
        price = round(el[1]['quote']['usd'.upper()]['price'], 2)
        percent1H = round(el[1]['quote']['usd'.upper()]['percent_change_1h'], 1)
        percent24H = round(el[1]['quote']['usd'.upper()]['percent_change_24h'], 1)
        cap = round(el[1]['quote']['usd'.upper()]['market_cap'], 1)
        a = f'{symbol}: {price}$ ({percent1H}%) [{percent24H}%]\nРыночная капитализация {symbol}: {cap}$' + '\n'
        answer_list.append(a)
    print('\n'.join(answer_list))


def request(slug, currency):
    answer = None
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
        answer = json.loads(r.text)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
    return answer


def sender():
    for element in dbData:
        T = element['period']
        schedule.every(T).minutes.do(message, element['tokens'].replace(' ', ''), element['currency'])
    while True:
        schedule.run_pending()
        time.sleep(1)

print(ts())
sender()