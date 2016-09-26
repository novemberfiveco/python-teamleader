import os
from ConfigParser import ConfigParser

import pytest

from teamleader.api import Teamleader


@pytest.fixture(scope='module')
def config():
    cfg = ConfigParser()
    cfg.read(os.path.join(os.path.expanduser('~'), '.teamleader', 'config'))
    return cfg


@pytest.fixture(scope='module')
def api(config):
    return Teamleader(config.get('teamleader', 'group'), config.get('teamleader', 'secret'))
