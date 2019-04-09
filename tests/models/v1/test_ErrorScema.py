# pylint: disable=protected-access
from source.models.v1 import ErrorSchema


def test_ErrorSchema_valid(): # noqa
    es = ErrorSchema()

    for propdescriptor in ErrorSchema._propertydescriptors:
        assert hasattr(es, propdescriptor.propertyname)