import requests
import json
from multiprocessing.dummy import Pool as ThreadPool

THREADS = 1000
TEST_URL = 'http://canihazip.com/s'
PROXY_PORTS = [8080, 45554, 3128, 1080, 80, 8888]

pool = ThreadPool(THREADS)

r = requests.get('http://pike.hqpeak.com/api/proxy').json()
proxies = []

for ip in r:
    proxies.extend(f'{ip}:{str(port)}' for port in PROXY_PORTS)
print(proxies)

count = 0
def check_proxy(proxy):
    global count
    count += 1
    print(count, len(proxies))

    _proxies = {'http': f'http://{proxy}', 'https': f'https://{proxy}'}
    try:
        r = requests.get(TEST_URL, proxies=_proxies, timeout=5)
        return { 'proxy': proxy, 'working': True }
    except Exception as e:
        print(e)
        return { 'proxy': proxy, 'working': False }


results = pool.map(check_proxy, proxies)

working = [result['proxy'] for result in results if result['working']]
with open('working.txt', 'w') as f:
    for proxy in working:
        f.write(proxy + '\n')