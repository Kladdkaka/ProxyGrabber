import requests
import re
import gzip
from xml.dom import minidom

proxy_regex = re.compile('(?:\d{1,3}\.){3}\d{1,3}:\d+')


def flatten(l):
    a = []

    for x in l:
        for z in x:
            a.append(z)

    return a


def hidester(): # broken
    r = requests.get('https://hidester.com/proxydata/php/data.php?mykey=csv&gproxy=2')

    proxies = []

    for proxy_data in r.json():
        proxies.append('{0}:{1}'.format(proxy_data['IP'], proxy_data['PORT']))

    return list(set(proxies))


def free_proxy_list():
    r = requests.get('http://free-proxy-list.appspot.com/proxy.json')

    proxies = []

    for proxy_data in r.json():
        proxies.append('{0}:{1}'.format(proxy_data['Host'], proxy_data['Port']))

    return list(set(proxies))


def xicidaili():
    r = requests.get('http://api.xicidaili.com/free2016.txt')

    proxies = r.text.splitlines()

    return list(set(proxies))


def orcatech(): # broken
    r = requests.get('https://orca.tech/?action=real-time-proxy-list')

    proxies = []
    allowed_chars = '0123456789:.'

    html = r.text

    raw_proxies = html[html.index('<button class="btn" data-clipboard-text="') + len(
        '<button class="btn" data-clipboard-text="'):html.index('"><i class="mdi-content-content-copy left">')]

    for line in raw_proxies.splitlines():
        proxy = ''

        for char in line:
            if char in allowed_chars:
                proxy += char

        proxies.append(proxy)

    return list(set(proxies))


def proxyape():
    r = requests.get('http://proxyape.com/')

    proxies = []

    html = r.text

    proxies = proxy_regex.findall(html)

    return list(set(proxies))


def proxyspy():
    r = requests.get('http://txt.proxyspy.net/proxy.txt')

    proxies = []

    html = r.text

    proxies = proxy_regex.findall(html)

    return list(set(proxies))


def cn_66ip():
    r = requests.get('http://www.66ip.cn/mo.php?tqsl=1000000')

    proxies = []

    html = r.text

    proxies = proxy_regex.findall(html)

    return list(set(proxies))


def proxyrss():
    r = requests.get('http://www.proxyrss.com/proxylists/all.gz')

    return list(set(gzip.decompress(r.content).decode('utf8').split()))


def proxylists():
    r = requests.get('http://www.proxylists.net/proxylists.xml')

    proxies = []

    xmldoc = minidom.parseString(r.text)

    for item in xmldoc.getElementsByTagName('prx:proxy'):
        proxies.append(
            item.getElementsByTagName('prx:ip')[0].firstChild.nodeValue + ':' + item.getElementsByTagName('prx:port')[
                0].firstChild.nodeValue)

    return list(set(proxies))


def proxz():
    r = requests.get('http://www.proxz.com/proxylists.xml')

    proxies = []

    xmldoc = minidom.parseString(r.text)

    for item in xmldoc.getElementsByTagName('prx:proxy'):
        proxies.append(
            item.getElementsByTagName('prx:ip')[0].firstChild.nodeValue + ':' + item.getElementsByTagName('prx:port')[
                0].firstChild.nodeValue)

    return list(set(proxies))


def rosinstrument():
    r1 = requests.get('http://tools.rosinstrument.com/proxy/plab100.xml')
    r2 = requests.get('http://tools.rosinstrument.com/proxy/l100.xml')

    xmlraw1 = r1.text
    xmlraw2 = r2.text

    proxies1 = proxy_regex.findall(xmlraw1)
    proxies2 = proxy_regex.findall(xmlraw2)

    proxies = list(set(proxies1 + proxies2))

    return proxies


def xroxy():
    r = requests.get('http://www.xroxy.com/proxyrss.xml')

    proxies = []

    xmldoc = minidom.parseString(r.text)

    for item in xmldoc.getElementsByTagName('prx:proxy'):
        proxies.append(
            item.getElementsByTagName('prx:ip')[0].firstChild.nodeValue + ':' + item.getElementsByTagName('prx:port')[
                0].firstChild.nodeValue)

    return list(set(proxies))


_proxies = flatten([
    #hidester(),
    free_proxy_list(),
    xicidaili(),
    #orcatech(),
    proxyape(),
    proxyspy(),
    cn_66ip(),
    proxyrss(),
    proxylists(),
    proxz(),
    rosinstrument(),
    xroxy()
])

print(len(_proxies))
print(len(list(set(_proxies))))

with open('proxies.txt', 'w') as f:
    f.write(
        '\n'.join(
            list(set(_proxies))
        )
    )
