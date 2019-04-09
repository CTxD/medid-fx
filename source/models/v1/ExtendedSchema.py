from typing import List

from . import BaseSchema
from . import DrugSchema
from . import PropertyDescriptor


class ExtendedSchema(BaseSchema):
    _propertydescriptors: List[PropertyDescriptor] = [
        PropertyDescriptor('name', str, ''),
        PropertyDescriptor('substance', str, ''),
        PropertyDescriptor('drugitems', List[DrugSchema], [])
    ]

    def __init__(self, **kwargs):
        super().__init__(self._propertydescriptors, **kwargs)