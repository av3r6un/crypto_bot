import json
import random
import time
from datetime import datetime
import pymysql
import schedule

coinName = []

# con = pymysql.connect(host='192.168.1.49',
#                       user='superuser',
#                       password='Alexander1a1',
#                       database='cryptobot_data',
#                       cursorclass=pymysql.cursors.DictCursor)


def top100():
    with open('data/top100tokens.json', 'r') as file:
        cryptoData = json.load(file)
    for data in cryptoData['data']:
        # tup = (data['symbol'], data['slug'])
        TopCoins = dict({data['symbol']:data['slug']})
        coinName.append(TopCoins)
    return coinName


def find_el(element):
    el = element
    slug = None
    for i in top100():
        for j in i.items():
            if j[0] == el:
                slug = j[1]
    return slug


def find_symbol(element):
    el = element
    symbol = None
    for i in top100():
        for j in i.items():
            if j[1] == el:
                symbol = j[0]
    return symbol


def replace(elem_list):
    output = []
    for el in elem_list:
        res = find_symbol(el)
        output.append(res)
    return output

