# pylint: disable=protected-access
from typing import List

import pytest

from source.models.v1 import PropertyDescriptor


class MockClass():
    prop1 = 'value1'
    prop2 = 22


def test_PropertyDescriptor_valid(): # noqa
    pd = PropertyDescriptor('name', str, 'default value')

    assert pd.propertyname == 'name'
    assert pd.propertytype == str
    assert pd.defaultvalue == 'default value'


def test_PropertyDescriptor_invalid_propertyname(): # noqa
    with pytest.raises(ValueError):
        PropertyDescriptor('', str, 'default value')


def test_PropertyDescriptor_invalid_propertytype(): # noqa
    with pytest.raises(ValueError):
        PropertyDescriptor('property', None, 'default value')


def test_PropertyDescriptor_inconsistent_propertytype_defaultvalue_type(): # noqa
    with pytest.raises(TypeError):
        PropertyDescriptor('property', int, 'invalid default type')
        PropertyDescriptor('property', str, 0)
        PropertyDescriptor('property', List[MockClass], [])