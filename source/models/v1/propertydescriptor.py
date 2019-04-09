from typing import Type, cast


class PropertyDescriptor():
    def __init__(self, propertyname: str, propertytype: Type, defaultvalue: object):
        if not propertyname or not propertytype:
            raise ValueError(
                f'Error instantiating PropertyDescriptor. One or more values are not properly set. '
                f'Name: {propertyname} -- Type: {propertytype}'
            )
        
        try:
            # Base types, e.g. str, bool, int, list
            if isinstance(propertytype, type) and not isinstance(defaultvalue, propertytype):
                raise Exception()

            # Complex types (provided by typing library), e.g. List[str]
            cast(propertytype, defaultvalue) # type: ignore
        except Exception as e:
            raise TypeError(
                f'Property {propertyname} has specified type {propertytype}, but the default '
                f'value has type {type(defaultvalue)}.\r\n'
                f'Inner exception: {e}'
            )
        
        self.propertyname = propertyname
        self.propertytype = propertytype
        self.defaultvalue = defaultvalue