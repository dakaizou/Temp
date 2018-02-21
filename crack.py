from bs4 import BeautifulSoup
from string import ascii_lowercase, ascii_uppercase
import urllib3
import re
import multiprocessing
import itertools

http = urllib3.PoolManager()

r = http.request('POST', 'http://anyinfo2you.com/811/', fields={'ans': '123'})
soup = BeautifulSoup(r.data, 'html.parser')

class Guess:
    def __init__(self, pool_manager, headers, answers_dict, answers_lock):
        self.answer = {'ans': None}
        self.header = headers
        self.http = pool_manager
        self.url = 'http://anyinfo2you.com/811/'
        self._result = re.compile('(\d+)A(\d+)B')
        self.answers_dict = answers_dict
        self.answers_lock = answers_lock

    def guess(self, answer):
        self.answer['ans'] = answer
        return self.submit()

    def submit(self):
        res = self.http.request('POST', self.url, fields=self.answer, headers=self.header)
        with self.answers_lock:
            self.answers_dict[self.answer['ans']] = self.parse(res.data)

    def parse(self, res):
        # centers = [c.text.split(' => ') for c in soup.find_all('center') if '=>' in c.text]
        result = BeautifulSoup(res, 'html.parser').find_all('center')[-1].text.split(' => ')[1]
        m = self._result.match(result)
        if m:
            a_number = int(m.group(1))
            b_number = int(m.group(2))
            if a_number == len(self.answer['ans']):
                print(self.answer['ans'])
            return (a_number + b_number), a_number, b_number
        raise Exception('shit happens')

class Question:
    def __init__(self, headers = None):
        self.header = headers
        self.pool_manager = urllib3.PoolManager()
        self.answer_length = self.get_char_number()
        self.manager = multiprocessing.Manager()
        self.answers_dict = self.manager.dict()
        self.answers_lock = multiprocessing.RLock()
        self.all_chars = '0123456789-_' + ascii_lowercase + ascii_uppercase

    def get_char_number(self):
        if self.header['Cookie'] != None:
            r = http.request('GET', 'http://anyinfo2you.com/811/', headers=self.header)
        else:
            r = http.request('GET', 'http://anyinfo2you.com/811/')
        return int(BeautifulSoup(r.data, 'html.parser').td.text.split()[0])

    def init_scan(self):
        reqs_number = int(len(self.all_chars) / self.answer_length)
        if len(self.all_chars) % self.answer_length != 0:
            reqs_number += 1

        guesses = []
        guess_threads = []

        for i in range(reqs_number):
            if i == reqs_number - 1:
                guess_string = self.all_chars[-self.answer_length:]
            else:
                offset = i * self.answer_length
                guess_string = self.all_chars[offset:offset + self.answer_length]

            guess = Guess(self.pool_manager, self.header, self.answers_dict, self.answers_lock)
            t = multiprocessing.Process(target=guess.guess, args=(guess_string,))
            guess_threads.append(t)
            t.start()

        for t in guess_threads:
            t.join()

        print(self.answers_dict)

    def perm(self, possible_answer_string):
        guesses = []
        guess_threads = []

        for p in itertools.permutations(possible_answer_string):
            s = ''.join(p)
            guess = Guess(self.pool_manager, self.header, self.answers_dict, self.answers_lock)
            t = multiprocessing.Process(target=guess.guess, args=(s,))
            guess_threads.append(t)
            t.start()
        for t in guess_threads:
            t.join()

        print(self.answers_dict)



# headers = {'Cookie': r.headers['Set-Cookie']}
# print(r.headers['Set-Cookie'])
headers = {'Cookie': 'PHPSESSID=fi0nmf4nrt4l1s3qtv5u59mm26; path=/'}

q = Question(headers)
q.init_scan()
# q.perm('izEGbeO5w')
