import codecs
import json
import threading
import time
from HTMLParser import HTMLParser

import urllib3
from bs4 import BeautifulSoup

results = []
urllib3.disable_warnings()
http = urllib3.PoolManager()
home = 'https://epv.afa.gov.tw'
with codecs.open('farm.json', encoding='utf-8') as input:
    data = json.load(input)
entries = data['rows']

def get_data(url):
    print(url)
    r = http.request('GET', url)
    return r.data

def parse(doc, entry, results):
    soup = BeautifulSoup(doc, 'html.parser')
    if entry['link'] == "/Home/FarmDetail":
        print(soup.table.find_all('td')[12].a.text)
        addr = soup.table.find_all('td')[12].a.text
    else:
        print(soup.table.find_all('td')[8].a.text)
        addr = soup.table.find_all('td')[8].a.text
    # TODO: return the original entry with entry['address']
    entry['addr'] = addr
    results.append(entry)


def run(entry, results):
    parse(get_data(home + entry['link'] + '/' + str(entry['ID'])), entry, results)

threads = []
for entry in entries:
    if 'FarmDetail' not in entry['link']:
        continue
    t = threading.Thread(target=run, args=(entry, results))
    threads.append(t)
    t.start()
    time.sleep(0.2)

for t in threads:
    t.join()

with codecs.open('result.json', mode='w', encoding='utf8') as output:
    h = HTMLParser()
    output.write(h.unescape(json.dumps(results, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)))
