from typing import List

from . import PropertyDescriptor


class BaseSchema():
    def __init__(self, properties: List[PropertyDescriptor], **kwargs):
        for propdesc in properties:
            propkey = propdesc.propertyname
            propvalue = propdesc.defaultvalue

            if propkey in kwargs:
                if not type(kwargs[propkey]) == propdesc.propertytype:
                    raise TypeError(
                        f'Invalid type instantiating property in {self.__class__.__name__}: '
                        f'The property {propkey} has type {propdesc.propertytype} but a type of '
                        f'{type(kwargs[propkey])} has been provided.'
                    )
                propvalue = kwargs[propkey]

            setattr(self, propkey, propvalue)
