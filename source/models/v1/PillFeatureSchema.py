from typing import List
from . import BaseSchema
from . import PropertyDescriptor


class PillFeature():
    def __init__(self, pillname: str, substance: str, shapeFeature: List[float], colour: str): # noqa
        self.pillname: str = pillname
        self.substance: str = substance
        self.shapeFeature: List[float] = shapeFeature
        self.colour: str = colour 
 

# class PillFeature(BaseSchema):
#     _propertydescriptors: List[PropertyDescriptor] = [
#         PropertyDescriptor('name', str, ''),
#         PropertyDescriptor('substance', str, ''),
#         PropertyDescriptor('shapeFeature', List[float], [])
#     ]

#     def __init__(self, **kwargs):
#         super().__init__(self._propertydescriptors, **kwargs)
