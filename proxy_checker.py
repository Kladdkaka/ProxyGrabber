import requests
import json
from multiprocessing.dummy import Pool as ThreadPool

THREADS = 1000
TEST_URL = 'http://canihazip.com/s'

pool = ThreadPool(THREADS)

with open('proxies.json', 'r') as f:
    proxies = json.load(f)

count = 0


def check_proxy(proxy):
    global count
    count += 1
    print(count, len(proxies))

    _proxies = {
        'http': 'http://' + proxy,
        'https': 'https://' + proxy
    }
    try:
        r = requests.get(TEST_URL, proxies=_proxies, timeout=5)
        return { 'proxy': proxy, 'working': True }
    except Exception as e:
        print(e)
        return { 'proxy': proxy, 'working': False }


results = pool.map(check_proxy, proxies)

working = []

for result in results:
    if result['working']:
        working.append(result['proxy'])

with open('working.txt', 'w') as f:
    for proxy in working:
        f.write(proxy + '\n')