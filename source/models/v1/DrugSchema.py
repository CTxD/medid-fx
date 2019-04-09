from typing import List

from . import BaseSchema
from . import PropertyDescriptor


class DrugSchema(BaseSchema):
    _propertydescriptors: List[PropertyDescriptor] = [
        PropertyDescriptor('kind', str, ''),
        PropertyDescriptor('strength', str, ''),
        PropertyDescriptor('imprint', List[str], []),
        PropertyDescriptor('score', str, ''),
        PropertyDescriptor('color', List[str], []),
        PropertyDescriptor('size', str, ''),
        PropertyDescriptor('image', str, '')
    ]

    def __init__(self, **kwargs):
        super().__init__(self._propertydescriptors, **kwargs)
    
