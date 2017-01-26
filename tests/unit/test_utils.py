import pytest

from teamleader.api import Teamleader
from teamleader.exceptions import InvalidInputError


def test_validate_type():
    for arg, t in ((['item'], list), ({'key': 'value'}, dict)):
        assert Teamleader._validate_type(arg, t) == arg

    for t in (list, dict):
        assert Teamleader._validate_type(None, t) == t()

    with pytest.raises(InvalidInputError):
        Teamleader._validate_type('not a list', list)


def test_convert_custom_fields():
    data = {
        'key': 'value',
        'custom_fields': {
            'key': 'value',
            'foo': 'bar'
        }
    }

    Teamleader._convert_custom_fields(data)

    assert data == {
        'key': 'value',
        'custom_field_key': 'value',
        'custom_field_foo': 'bar'
    }
