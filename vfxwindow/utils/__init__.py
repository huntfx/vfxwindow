from __future__ import absolute_import

import os
from functools import wraps

if os.name == 'nt':
    from .windows import setCoordinatesToScreen
else:
    def setCoordinatesToScreen(x, y, *args):
        return (x, y)


class hybridmethod(object):
    """Merge a normal method with a classmethod.
    The first two arguments are (cls, self), where self will match cls if it is a classmethod.

    Source: https://stackoverflow.com/a/18078819/2403000
    """
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls):
        context = obj if obj is not None else cls

        @wraps(self.func)
        def hybrid(*args, **kw):
            return self.func(cls, context, *args, **kw)

        # Mimic method attributes (not required)
        hybrid.__func__ = hybrid.im_func = self.func
        hybrid.__self__ = hybrid.im_self = context

        return hybrid
