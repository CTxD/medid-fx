# pylint: disable=protected-access
from source.models.v1 import ExtendedSchema


def test_ExtendedSchema_valid(): # noqa
    es = ExtendedSchema()

    for propdescriptor in ExtendedSchema._propertydescriptors:
        assert hasattr(es, propdescriptor.propertyname)