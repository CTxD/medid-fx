from typing import List

from . import BaseSchema
from . import DrugSchema
from . import PropertyDescriptor


class SlimSchema(BaseSchema):
    _propertydescriptors: List[PropertyDescriptor] = [
        PropertyDescriptor('name', str, ''),
        PropertyDescriptor('substance', str, '')
    ] + DrugSchema._propertydescriptors # noqa

    def __init__(self, **kwargs):
        super().__init__(self._propertydescriptors, **kwargs)