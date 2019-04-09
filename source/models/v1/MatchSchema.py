from typing import List

from . import BaseSchema
from . import SlimSchema
from . import PropertyDescriptor


class MatchSchema(BaseSchema):
    _propertydescriptors: List[PropertyDescriptor] = [
        PropertyDescriptor('confidence', float, 0.0)
    ] + SlimSchema._propertydescriptors # noqa

    def __init__(self, **kwargs):
        super().__init__(self._propertydescriptors, **kwargs)