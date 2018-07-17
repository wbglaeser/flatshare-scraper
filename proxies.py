#-------------------------------------
# Import Modules
#-------------------------------------
from bs4 import BeautifulSoup
from urllib.request import urlopen, HTTPError, Request
from fake_useragent import UserAgent

#-------------------------------------
# Set up Variables
#-------------------------------------
ua = UserAgent()

#-------------------------------------
# Fetch Data
#-------------------------------------
class ProxyScrawler():

    def define_request(self):
        req = Request(
            'https://sslproxies.org/',
            headers={
                'User-Agent': ua.random
                }
            )
        return req

    def open_url(self, req):
        try:
            html = urlopen(req)
            return html
        except HTTPError as e:
            print(e)

    def parse_url(self, html):
        try:
            soup = BeautifulSoup(html, 'lxml')
            return soup
        except BaseException as e:
            print(e)

    def save_proxies(self, soup):
        proxies = []
        proxies_table = soup.find(id='proxylisttable')
        for row in proxies_table.tbody.find_all('tr'):
            if row.find_all('td')[4].string == 'elite proxy' \
                    and row.find_all('td')[6].string == 'yes':
                proxies.append(
                    {
                        'ip': row.find_all('td')[0].string,
                        'port': row.find_all('td')[1].string,
                    }
                )
        return proxies

    def return_proxy_dict(self):
        req = self.define_request()
        raw_html = self.open_url(req)
        soup = self.parse_url(raw_html)
        proxy_list = self.save_proxies(soup)
        return proxy_list

