import os
import pytest

import requests
import vcr
from wwsync.weight_watchers import login

CASSETTES_HOME = "{}/fixtures/vcr_cassettes".format(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="session")
def session():
    with vcr.use_cassette("{}/{}.yaml".format(CASSETTES_HOME, 'login')):
        return login(os.environ['WW_USER'], os.environ['WW_PASSWD'], requests.Session())
