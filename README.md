# TornadoWordCounter
### Installing

1) Install python dependencies:

```
pip install -r requirement.txt
```

2) Generate public/private keys:

```
python keys/generate_keys.py
```

3) Run server:

```
python server.py
```

### Key storage

In this example and for demo purposes the public/private keys are stored on a folder in the same project directory, the best approach to store these keys would be to use a system cryptographic library with passphrase.

### Notes

I wasn't able to access App Engine because it doesn't accept debit or prepaid cards, so I hosted the code on my personal server. Access >>
```
http://vps236770.ovh.net:8888/
```

I've done several commits so it can be possible to control the resolution times. 11h initial commit - 19h final commit, I've done a few stops and counting on reading the Tornado API gives about 6h-7h of work. I've used SQLite so I wouldn't need to install MySQL on my server, but since they are similar in terms of code there shouldn't be any problem, anyway I left some lines in comments and the schema in case of need to apply MySQL.
