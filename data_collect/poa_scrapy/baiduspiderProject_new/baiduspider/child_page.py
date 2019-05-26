# -*- coding: utf-8 -*-
import requests
from lxml import etree
def child_page(child_url,method='get',is_headers=False,send_headers=None):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0'}
    headers = send_headers if send_headers!=None else headers
    if method=='get' and is_headers:
        response = requests.get(child_url, headers=headers)
    elif method=='get':
        response = requests.get(child_url)
    elif method=='post' and is_headers:
        response = requests.post(child_url, headers=headers)
    elif method=='post':
        response = requests.post(child_url)
    root = etree.HTML(response.content)
    return root