# pylint: disable=protected-access
from source.models.v1 import MatchSchema


def test_MatchSchema_valid(): # noqa
    ms = MatchSchema()

    for propdescriptor in MatchSchema._propertydescriptors:
        assert hasattr(ms, propdescriptor.propertyname)