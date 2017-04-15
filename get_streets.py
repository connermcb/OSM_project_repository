# -*- coding: utf-8 -*-
"""
Web Scraper
"""
from lxml import html
import re
import requests
import string

page = requests.get('http://www.geographic.org/streetview/usa/tx/austin.html')
tree = html.fromstring(page.content)


def write_streets_dict(url):
    d= {letter:[] for letter in string.ascii_lowercase}
    page = requests.get(url)
    tree = html.fromstring(page.content)
    for i in range(1, 8763):
        print(i)
        street = tree.xpath('/html/body/div[3]/div/span/ul/li[{}]/a/text()'.format(i))[0]
        first = street[0]
        if type(first) == int:
            continue
        if first.lower() in d:
            d[first.lower()].append(street)
    return d

    
print(write_streets_dict('http://www.geographic.org/streetview/usa/tx/austin.html').items())





#'http://www.geographic.org/streetview/usa/tx/austin.html'