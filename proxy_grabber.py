import re
from xml.dom import minidom

from requests import Session as WebClient
from pyquery import PyQuery

proxy_regex = re.compile('(?:\d{1,3}\.){3}\d{1,3}:\d+')

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
                    site_proxies = set(func(WebClient(), url))
                except ValueError:
                    print('URL %s failed' % url)
                    raise
                proxies.update(site_proxies)
                print('got %d proxies from %s, now: %d' % (len(site_proxies), name, len(proxies)))
        return proxies

def by_linesplit(client, url):
    return client.get(url).text.splitlines()

def by_json_dicts(host_key, port_key):
    def _by_json_dicts(client, url):
        for data in client.get(url).json():
            yield '%s:%s' % (data[host_key], data[port_key])
    return _by_json_dicts

def by_regex(client, url):
    return proxy_regex.findall(client.get(url).text)

def by_regex_for_first_link_with_proxies(client, url):
    response = client.get(url)
    for link in PyQuery(response.text, parser='html').items('a'):
        lurl = url + link.attr.href
        print('get proxies from', lurl, end='\r')
        proxies = set(by_regex(client, lurl))
        print('got %d proxies from %s' % (len(proxies), lurl))
        if proxies:
            return proxies

def by_gziputf8split(client, url):
    return gzip.decompress(client.get(url).content).decode('utf8').split()

def by_xmldom(client, url):
    xmldoc = minidom.parseString(client.get(url).text)
    for item in xmldoc.getElementsByTagName('prx:proxy'):
        yield '%s:%s' % (item.getElementsByTagName('prx:ip')[0].firstChild.nodeValue,
                         item.getElementsByTagName('prx:port')[0].firstChild.nodeValue)


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


# grab.orcatech = 'https://orca.tech/?action=real-time-proxy-list', by_orcatech_html, 0  # dead

#=======================================================================================================================
# def by_orcatech_html(client, url):
#     fstr, tstr = '<button class="btn" data-clipboard-text="', '"><i class="mdi-content-content-copy left">'
#     html = client.get(url).text
#     for line in html[html.index(fstr) + len(fstr):html.index(tstr)].splitlines():
#         proxy = ''
#         for char in line:
#             if char in '0123456789:.':
#                 proxy += char
#         if proxy:
#             yield proxy
#=======================================================================================================================
