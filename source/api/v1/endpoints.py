from typing import Union

from ...fx import fx # type: ignore # noqa
from ...medinfo import extended, slim # type: ignore # noqa
from ...models.v1 import MatchSchema, ExtendedSchema, SlimSchema, MetaSchema, ErrorSchema # type: ignore # noqa
 
# Each of these functions are the actual endpoints. Their responsibility is to return an appropriate
# response back to the client. No domain logic should be contained in here, instead all of these 
# functions should call a seperate function which does the domain logic. These functions then return
# the response along with the HTTP Status code.
# Example: 
#   return response, 200


# Delegate for /api/v1/fx
def fx_matches(imageencoding) -> Union[ErrorSchema, MatchSchema]:
    return fx.getmatches(imageencoding)


# Delegate for /api/v1/medinfo/extended/{name}
def medinfo_extended(name) -> Union[ErrorSchema, ExtendedSchema]:
    return extended.getextended(name)


# Delegate for /api/v1/medinfo/slim/
def medinfo_slim() -> Union[ErrorSchema, SlimSchema]:
    return slim.getslim()


# Delegate for /api/v1/generate/{authtoken}
def generate_model(authtoken):
    return authtoken, 403


# Delegate for /api/v1/meta
def meta() -> Union[ErrorSchema, MetaSchema]:
    import time
    return 'v1.' + str(int(time.time()))
