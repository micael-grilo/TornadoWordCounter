#!/usr/bin/env python

import os.path, re, nltk, ast
import sqlite3, uuid, hashlib

from BeautifulSoup import BeautifulSoup 
from collections import Counter, OrderedDict
from Crypto.PublicKey import RSA

from tornado import gen, ioloop, web
from tornado.httpclient import AsyncHTTPClient
from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)
#define("mysql_host", default="127.0.0.1:3306", help="blog database host")
#define("mysql_database", default="words", help="blog database name")
#define("mysql_user", default="user", help="blog database user")
#define("mysql_password", default="password", help="blog database password")


########################################################
# -----    Application Salt and DB Connection -------- #
########################################################

#salt = uuid.uuid4().hex
salt = '3be5a66a0fe14e0883157b13697afe2a'

conn = sqlite3.connect('database/words.db')
c = conn.cursor()
try:
    c.execute('''CREATE TABLE words (id text, word BLOB, count int)''')
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
        self.render("index.html", title="Home Page", words = getWordsFromDB())

    @gen.coroutine
    def post(self):
        http_client = AsyncHTTPClient()
        response = yield http_client.fetch(self.get_body_argument("url"))
        saveWords(GetPageWords(response.body))
        self.render("index.html", title="Home Page", words = getWordsFromDB())

class AdminHandler(web.RequestHandler):
    def get(self):
        words = OrderedDict(sorted(getWordsFromDB().items(), key=lambda x: x[1], reverse=True))
        self.render("admin.html", title="Admin Page", words = words)


########################################################
# -------------    Application Utilities ------------- #
########################################################

def GetPageWords(body):
    '''
    Parse page looking for words,
    Return top 100 nouns and verbs only
    '''
    soup = BeautifulSoup(body)
    [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
    visible_text_string = soup.getText()
    lst = re.findall(r'\b\w+\b', visible_text_string)
    tokens = nltk.word_tokenize(' '.join(lst).lower())
    tagged = nltk.pos_tag(tokens)
    nouns = [word.encode('utf-8') for word,pos in tagged if (pos == 'NN' or pos == 'VB')]
    counter = Counter(nouns)
    occs = [(word,count) for word,count in counter.most_common(100)]
    return occs

def saveWords(words):
    '''
    Save words in DB
    Key : hashed salted word
    Word : Encrypted word with public key
    Count : Word count
    '''
    publickey = open('keys/public.key', "r")
    encryptor = RSA.importKey(publickey)
    for word, value in words:
        word_id = str(hashlib.sha1(salt.encode() + word.encode()).hexdigest())
        word_encrypted = encryptor.encrypt(str(word),32)
        count = value
        c.execute("SELECT count FROM words WHERE id=?", (word_id,))
        rows = c.fetchone()
        if rows:
            c.execute("UPDATE words SET count = ? WHERE id = ? ", ((count+rows[0]), word_id))
        else:
            c.execute("INSERT INTO words VALUES (?, ?, ?)", (word_id, sqlite3.Binary(str(word_encrypted)), count))
    conn.commit()


def getWordsFromDB():
    '''
    Retrieve words from DB
    '''
    word_dict = {}
    privatekey = open('keys/private.key', "r")
    decryptor = RSA.importKey(privatekey)
    c.execute("SELECT word, count FROM words ORDER BY Count DESC LIMIT 100")
    rows = c.fetchall()
    for row in rows:
        word = decryptor.decrypt(ast.literal_eval(str(row[0])))
        word_dict[word] = row[1]
    return word_dict


########################################################
# -------------    Application Main ------------------ #
########################################################

if __name__ == "__main__":
    #nltk.download('punkt')
    #nltk.download('averaged_perceptron_tagger')
    app = Application()
    app.listen(options.port)
    ioloop.IOLoop.current().start()