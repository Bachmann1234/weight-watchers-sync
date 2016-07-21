import os

from cryptography.fernet import Fernet

CIPHER_SUITE = Fernet(os.environ['WW_SYNC_ENCRYPTION_KEY'])


def encrypt(msg):
    return CIPHER_SUITE.encrypt(msg)


def decrypt(msg):
    return CIPHER_SUITE.decrypt(msg)
