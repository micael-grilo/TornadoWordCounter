#!/usr/bin/env python

import os.path, re, nltk

from BeautifulSoup import BeautifulSoup 
from collections import Counter
import sqlite3, uuid, hashlib

from tornado import gen, ioloop, web
from tornado.httpclient import AsyncHTTPClient
from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)
#define("mysql_host", default="127.0.0.1:3306", help="blog database host")
#define("mysql_database", default="words", help="blog database name")
#define("mysql_user", default="user", help="blog database user")
#define("mysql_password", default="password", help="blog database password")

salt = uuid.uuid4().hex
print salt
conn = sqlite3.connect('words.db')
c = conn.cursor()
try:
    c.execute('''CREATE TABLE words (id text, word text, count int)''')
except sqlite3.OperationalError:
    pass

########################################################
# -------------    Application Core ------------------ #
########################################################

class Application(web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/admin", AdminHandler)
        ]
        settings = {
            "debug": True,
            "template_path": os.path.join(os.path.dirname(__file__),"templates"),
            "static_path": os.path.join(os.path.dirname(__file__),"static")
        }
        web.Application.__init__(self, handlers, **settings)
        '''self.db = torndb.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)'''


class MainHandler(web.RequestHandler):
    def get(self):
        self.render("index.html", title="My title")

    @gen.coroutine
    def post(self):
        self.set_header("Content-Type", "text/plain")
        self.write("You wrote " + self.get_body_argument("url"))
        http_client = AsyncHTTPClient()
        response = yield http_client.fetch(self.get_body_argument("url"))
        saveWords(top100_webPageWords(response.body))
        #self.render("index.html", title="Results")

class AdminHandler(web.RequestHandler):
    def get(self):
        self.render("index.html", title="My title")


########################################################
# -------------    Application Utilities ------------- #
########################################################

def top100_webPageWords(body):
    soup = BeautifulSoup(body)
    visible_text_string = soup.getText()
    lst = re.findall(r'\b\w+\b', visible_text_string)
    tokens = nltk.word_tokenize(' '.join(lst).lower())
    tagged = nltk.pos_tag(tokens)
    nouns = [word for word,pos in tagged if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS')]
    words = [x.encode('utf-8') for x in nouns]
    counter = Counter(words)
    occs = [(word,count) for word,count in counter.most_common(100)]
    return occs

def saveWords(words):
    print len(words)
    for word, value in words:
        word_id = hashlib.sha1(salt.encode() + word.encode()).hexdigest()
        word_encr = word
        count = value
        print word_id, word, count
        #c.execute("insert into words values (?, ?, ?)", (word_id, word_encr, count))
    conn.commit()





if __name__ == "__main__":
    #nltk.download('punkt')
    #nltk.download('averaged_perceptron_tagger')
    app = Application()
    app.listen(options.port)
    ioloop.IOLoop.current().start()