import os
import pytest

import requests
import vcr
from wwsync.weight_watchers import login

FIXTURES_HOME = "{}/fixtures".format(os.path.dirname(os.path.abspath(__file__)))
CASSETTES_HOME = "{}/vcr_cassettes".format(FIXTURES_HOME)


@pytest.fixture(scope="session")
def session(username, password):
    with vcr.use_cassette("{}/{}.yaml".format(CASSETTES_HOME, 'login')):
        return login(username, password, requests.Session())


@pytest.fixture(scope="session")
def username():
    return os.environ['WW_USER']


@pytest.fixture(scope="session")
def password():
    return os.environ['WW_PASSWD']

