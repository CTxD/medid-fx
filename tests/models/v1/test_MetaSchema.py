# pylint: disable=protected-access
from source.models.v1 import MetaSchema


def test_MetaSchema_valid(): # noqa
    ms = MetaSchema()

    for propdescriptor in MetaSchema._propertydescriptors:
        assert hasattr(ms, propdescriptor.propertyname)