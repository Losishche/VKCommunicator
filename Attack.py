__author__ = 'grishaev'

import requests

addr = 'http://www.arthurpokrovskiy.ru'

while True:
    print(requests.request(url=addr, method='get'))
