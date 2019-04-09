# pylint: disable=protected-access
from source.models.v1 import SlimSchema


def test_SlimSchema_valid(): # noqa
    ss = SlimSchema()

    for propdescriptor in SlimSchema._propertydescriptors:
        assert hasattr(ss, propdescriptor.propertyname)