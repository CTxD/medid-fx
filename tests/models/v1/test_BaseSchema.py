import pytest

from source.models.v1 import BaseSchema
from source.models.v1 import PropertyDescriptor


def test_baseschema_empty_propertydescriptors():
    bs = BaseSchema([])
    assert [attr for attr in dir(bs) if not attr.startswith('_')] == []


def test_baseschema_property_in_kwargs():
    bs = BaseSchema(
        [PropertyDescriptor('property1', str, 'default value')], 
        property1='Non-default value'
    )

    assert [attr for attr in dir(bs) if not attr.startswith('_')] == ['property1']
    assert bs.property1 == 'Non-default value'


def test_baseschema_inconsistent_types():
    with pytest.raises(TypeError):
        BaseSchema(
            [PropertyDescriptor('property1', int, 0)], 
            property1='Invalid type'
        )