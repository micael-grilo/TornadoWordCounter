from os import chmod
from Crypto.PublicKey import RSA
from Crypto import Random

random_generator = Random.new().read
key = RSA.generate(2048, random_generator)
with open("private.key", 'w') as content_file:
    chmod("private.key", 0600)
    content_file.write(key.exportKey('PEM'))
pubkey = key.publickey()
with open("public.key", 'w') as content_file:
    content_file.write(pubkey.exportKey('PEM'))