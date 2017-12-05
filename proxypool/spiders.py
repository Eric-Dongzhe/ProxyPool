"""爬虫模块，包含`SpiderMeta`类和一些初始的
爬虫类，如果用户需要定义自己的爬虫类，必须要继承
`SpiderMeta`类，并重写`gets`方法，`gets`
方法要求返回 ip:port 形式的代理。
"""
import logging
import re

import requests

from conf.settings import settings as psettings
from conf.settings import A3_LIST

from .errors import RewriteSpiderError
from .utils import get_page
import time


class SpiderMeta(type):
    spiders = []

    def _init(cls):
        """子类的构造方法
        :return: None
        """
        cls._counter = 1

    def _increment(cls, count):
        """子类用于增加计数器的方法
        :param count: 计数器增加量
        :return: None
        """
        cls._counter += count

    def _flush(cls):
        """计数器刷新为 1
        :return: None
        """
        cls._counter = 1

    def __new__(cls, *args, **kwargs):
        """构造子类
        :param args: args[0] = name, args[1] = bases, args[2] = attrs.
        :param kwargs: No.
        :return: 新类
        """

        # 爬虫类必须要有 `get` 方法。
        if 'gets' not in args[2]:
            raise RewriteSpiderError(args[0])

        # 给爬虫类添加一些默认方法
        args[2]['__init__'] = lambda self: SpiderMeta._init(self)
        args[2]['increment'] = lambda self, count: SpiderMeta._increment(self, count)
        args[2]['flush'] = lambda self: SpiderMeta._flush(self)

        # 将爬虫类加入到 `spiders` 列表中
        SpiderMeta.spiders.append(type.__new__(cls, *args, **kwargs))
        return type.__new__(cls, *args, **kwargs)


# def get_page(url):
#     html = ''
#     try:
#         # API调用限速
#         # 调用API
#         html = requests.get(url, timeout=300).content
#     except Exception as e:
#         logging.error('Exception in ADSLProxyManager.__api__call():{}'.format(str(e)))
#     return html.decode()


# class ProxyKunPengSpider(metaclass=SpiderMeta):
#
#     current_ip_url = '{}/un-ip/?token={}&username={}'
#     redial_ip_url = '{}/re-dial/?token={}&username={}'
#
#     def __api_call(self, url):
#         """调用API返回内容
#         """
#         html = ''
#         try:
#             # API调用限速
#             # 调用API
#             html = get_page(url)
#         except Exception as e:
#             # common.logger.error('Exception in ADSLProxyManager.__api__call():{}'.format(str(e)))
#             pass
#         return html
#
#     def get_one(self, a3):
#         username, api_url, token = a3.split(',')
#         url = self.current_ip_url.format(api_url, token, username)
#         # print(url)
#         ip = None
#         while True:  # 死循环，直到调用成功
#             html = self.__api_call(url)
#             if html:
#                 print(html)
#                 m = re.compile(r'"ip"\s*:\s*"([^\"]+)"').search(html)
#                 if m:
#                     ip = m.groups()[0]
#                 return ip
#
#     def gets(self, page_total=None):
#         # PROXY_USERNAME = 'kunzhipeng'
#         # PROXY_PASSWORD = 'kunzhipeng2013'
#         # PROXY_PORT = '8888'
#         PROXY_USERNAME = psettings['PROXY_USERNAME']
#         PROXY_PASSWORD = psettings['PROXY_PASSWORD']
#         PROXY_PORT = psettings['PROXY_PORT']
#
#         ans = []
#         for a3 in A3_LIST:
#             ip = self.get_one(a3)
#             ip = '{}:{}@{}:{}'.format(PROXY_USERNAME, PROXY_PASSWORD, ip, PROXY_PORT)
#             ans.append(ip)
#             return ans

class Proxy360Spider(metaclass=SpiderMeta):
    start_url = 'http://www.proxy360.cn/default.aspx'

    def gets(self, page_total=None):
        ans = []
        soup = get_page(self.start_url)
        for proxy in soup.find_all('div', {'class': 'proxylistitem'}):
            item = proxy.find_all('span', {"class": "tbBottomLine"})
            ip = item[0].get_text().replace('\r\n', '').replace(' ', '')
            port = item[1].get_text().replace('\r\n', '').replace(' ', '')
            ans.append(':'.join([ip, port]))
        return ans


class Daili666Spider(metaclass=SpiderMeta):
    start_url = 'http://www.66ip.cn/{}.html'

    def gets(self, page_total=3):
        urls = [self.start_url.format(i)
                for i in range(self._counter, self._counter + page_total)]
        self._counter += page_total
        ans = []
        for url in urls:
            soup = get_page(url)
            # 防止被 Ban, 加 1s 的间隔。
            time.sleep(1)
            proxy_list = soup.find('table', {"border": "2px"})
            for proxy in proxy_list.find_all('tr')[1:]:
                ip = proxy.find_all('td')[0].get_text()
                port = proxy.find_all('td')[1].get_text()
                ans.append(':'.join([ip, port]))
        return ans


class KuaidailiSpider(metaclass=SpiderMeta):
    start_url = 'http://www.kuaidaili.com/free/inha/{}/'

    def gets(self, page_total=2):
        urls = [self.start_url.format(i)
                for i in range(self._counter, self._counter + page_total)]
        self._counter += page_total
        ans = []
        for url in urls:
            soup = get_page(url)
            time.sleep(1)
            proxy_list = soup.find('table',
                                   {'class': 'table table-bordered table-striped'}) \
                .find('tbody')
            for proxy in proxy_list.find_all('tr'):
                tmp = proxy.find_all('td')
                ip = tmp[0].get_text()
                port = tmp[1].get_text()
                ans.append(':'.join([ip, port]))
        return ans


class XiciSpider(metaclass=SpiderMeta):
    start_url = 'http://www.xicidaili.com/nn/{}'

    def gets(self, page_total=2):
        urls = [self.start_url.format(i)
                for i in range(self._counter, self._counter + page_total)]
        self._counter += page_total
        ans = []
        for url in urls:
            soup = get_page(url)
            time.sleep(1)
            proxy_list = soup.find('table', {'id': 'ip_list'}) \
                             .find_all('tr')[1:]
            for proxy in proxy_list:
                tmp = proxy.find_all('td')
                ip = tmp[1].get_text()
                port = tmp[2].get_text()
                ans.append(':'.join([ip, port]))
        return ans

# 请在此处继续扩展你的爬虫类。