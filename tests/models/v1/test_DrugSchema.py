# pylint: disable=protected-access
from source.models.v1 import DrugSchema


def test_DrugSchema_valid(): # noqa
    ds = DrugSchema()

    for propdescriptor in DrugSchema._propertydescriptors:
        assert hasattr(ds, propdescriptor.propertyname)