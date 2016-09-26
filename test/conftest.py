import os

import pytest
import yaml

from teamleader.api import Teamleader


@pytest.fixture(scope='module')
def config():
    with open(os.path.join(os.path.expanduser('~'), '.teamleader', 'config.yml')) as f:
        return yaml.safe_load(f)['teamleader']


@pytest.fixture(scope='module')
def api(config):
    return Teamleader(config['group'], config['secret'])
