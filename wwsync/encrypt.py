import os

from cryptography.fernet import Fernet

CIPHER_SUITE = Fernet(os.environ['encryption_key'])


def encrypt(msg):
    return CIPHER_SUITE.encrypt(msg)

def decrypt(msg):
    return CIPHER_SUITE.decrypt(msg)
