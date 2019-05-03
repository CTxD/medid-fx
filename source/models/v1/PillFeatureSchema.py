from typing import List
from . import BaseSchema
from . import PropertyDescriptor

"""   def __init__(self, pillname: str, substance: str, colourFeature: List[ColourFeature], shapeFeature: List[ShapeFeature]): # noqa
        self.pillname = pillname
        self.substance = substance
        self.shapeFeature: List[float] = shapeFeature
 """


class PillFeature(BaseSchema):
    _propertydescriptors: List[PropertyDescriptor] = [
        PropertyDescriptor('name', str, ''),
        PropertyDescriptor('substance', str, ''),
        PropertyDescriptor('shapeFeature', List[float], [])
    ]

    def __init__(self, **kwargs):
        super().__init__(self._propertydescriptors, **kwargs)
