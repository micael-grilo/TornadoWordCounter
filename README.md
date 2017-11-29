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
