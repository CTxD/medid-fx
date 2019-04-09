from typing import List

from . import BaseSchema
from . import PropertyDescriptor


class ErrorSchema(BaseSchema):
    _propertydescriptors: List[PropertyDescriptor] = [
        PropertyDescriptor('message', str, '')
    ]

    def __init__(self, **kwargs):
        super().__init__(self._propertydescriptors, **kwargs)