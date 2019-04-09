from typing import List

from . import BaseSchema
from . import PropertyDescriptor


class MetaSchema(BaseSchema):
    _propertydescriptors: List[PropertyDescriptor] = [
        PropertyDescriptor('model', str, '')
    ]

    def __init__(self, **kwargs):
        super().__init__(self._propertydescriptors, **kwargs)