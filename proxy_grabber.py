import re
import gzip
import datetime
import requests
import json

from xml.dom import minidom

from pyquery import PyQuery
from multiprocessing.dummy import Pool as ThreadPool

proxy_regex = re.compile('(?:\d{1,3}\.){3}\d{1,3}:\d+')

pool = ThreadPool(10)


class ProxyGrab:
    def __init__(self):
        self._sites = {}

    def __getattr__(self, name):
        try:
            return self._sites[name.upper()]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            return super().__setattr__(name, value)
        value = value if len(value) == 3 else value + (True,)
        self._sites[name.upper()] = value

    def __iter__(self):
        return iter((n,) + vs for n, vs in self._sites.items())

    def __dir__(self):
        return super().__dir__() + list(self._sites)

    def get_proxies(self, *names):
        proxies, names = set(), {n.upper() for n in names}
        for name, url, func, enabled in self:
            if (names and name in names) or (not names and enabled):
                print('get proxies from', name, end='\r')
                try:
                    site_proxies = set(func(url))
                except ValueError:
                    print('URL %s failed' % url)
                    raise
                proxies.update(site_proxies)
                print('got %d proxies from %s, now: %d' % (len(site_proxies), name, len(proxies)))
        return list(proxies)


def by_linesplit(url):
    return requests.get(url).text.splitlines()


def by_json_dicts(host_key, port_key):
    def _by_json_dicts(url):
        for data in requests.get(url).json():
            yield '%s:%s' % (data[host_key], data[port_key])
    return _by_json_dicts


def by_regex(url):
    r = requests.get(url).text
    return proxy_regex.findall(r)


def by_regex_for_first_link_with_proxies(url):
    response = requests.get(url)
    for link in PyQuery(response.text, parser='html').items('a'):
        lurl = url + link.attr.href
        print('get proxies from', lurl, end='\r')
        proxies = set(by_regex(lurl))
        print('got %d proxies from %s' % (len(proxies), lurl))
        if proxies:
            return proxies


def by_gziputf8split(url):
    return gzip.decompress(requests.get(url).content).decode('utf8').split()


def by_xmldom(url):
    xmldoc = minidom.parseString(requests.get(url).text)
    for item in xmldoc.getElementsByTagName('prx:proxy'):
        yield '%s:%s' % (item.getElementsByTagName('prx:ip')[0].firstChild.nodeValue,
                         item.getElementsByTagName('prx:port')[0].firstChild.nodeValue)


def by_checkerproxy(baseurl):
    urls = []
    dates = []
    proxies = []

    for days in range(0, 7):
        dates.append(datetime.datetime.now() - datetime.timedelta(days=days))

    for date in dates:
        urls.append(baseurl + date.strftime('%Y-%m-%d'))

    results = pool.map(by_regex, urls)

    for proxy_list in results:
        proxies.extend(proxy_list)

    return list(set(proxies))

grab = ProxyGrab()

grab.hidester = 'https://hidester.com/..', by_json_dicts('IP', 'PORT'), 0  # filters, pagination and json, not now
grab.free_proxy_list = 'http://free-proxy-list.appspot.com/proxy.json', by_json_dicts('Host', 'Port')
grab.xicidaili = 'http://api.xicidaili.com/free2016.txt', by_linesplit
grab.proxyape = 'http://proxyape.com/', by_regex
grab.proxyspy = 'http://txt.proxyspy.net/proxy.txt', by_regex, 0  # dunno, takes too long
grab.cn_66ip = 'http://www.66ip.cn/mo.php?tqsl=1000000', by_regex
grab.proxyrss = 'http://www.proxyrss.com/proxylists/all.gz', by_gziputf8split
grab.proxylists = 'http://www.proxylists.net/proxylists.xml', by_xmldom
grab.proxz = 'http://www.proxz.com/proxylists.xml', by_xmldom
grab.rosinstrument1 = 'http://tools.rosinstrument.com/proxy/plab100.xml', by_regex
grab.rosinstrument2 = 'http://tools.rosinstrument.com/proxy/l100.xml', by_regex
grab.xroxy = 'http://www.xroxy.com/proxyrss.xml', by_xmldom
grab.orcatech = 'https://orca.tech/community-proxy-list/', by_regex_for_first_link_with_proxies
grab.checkerproxy = 'https://checkerproxy.net/api/archive/', by_checkerproxy
grab.freevpn_ninja = 'https://freevpn.ninja/free-proxy/txt', by_regex

with open('proxies.json', 'w') as f:
    f.write(json.dumps(grab.get_proxies()))