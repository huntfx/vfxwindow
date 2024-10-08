from __future__ import absolute_import

import __main__
import inspect
import json
import os
import site
import sys
import tempfile
from functools import wraps
from types import ModuleType

if os.name == 'nt':
    from .windows import setCoordinatesToScreen
else:
    def setCoordinatesToScreen(x, y, *args, **kwargs):
        return (x, y)


SITE_PACKAGES = site.getsitepackages()


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


def searchGlobals(cls, globalsDict=None, visited=None):
    """Search from the top level globals for a particular object.
    Every time a module is found, search that too.
    """
    if globalsDict is None:
        # Read the globals from `__main__`
        # Originally this used `inspect.stack()[-1][0].f_globals`, but
        # anything launched in Nuke's startup would not be under the
        # main stack and would cause this to fail.
        globalsDict = __main__.__dict__

    # Initially mark every builtin module as visisted
    if visited is None:
        visited = set(filter(bool, map(sys.modules.get, sys.builtin_module_names)))

    recursiveSearch = {}
    for k, v in globalsDict.items():
        if v is cls:
            return k

        elif isinstance(v, ModuleType) and v not in visited:
            visited.add(v)

            #Check it's not a built in module
            try:
                modulePath = inspect.getsourcefile(v)
            except TypeError:
                continue

            # Skip any installed modules
            if modulePath is None or any(modulePath.startswith(i) for i in SITE_PACKAGES):
                continue

            recursiveSearch[k] = v.__dict__

    # Recursively search submodules
    for k, v in recursiveSearch.items():
        result = searchGlobals(cls, v, visited=visited)
        if result:
            return k + '.' + result


class CustomEncoder(json.JSONEncoder):
    """JSON encoder that allows registering classes.

    Usage:
        >>> class MyClass(object): ...
        >>> CustomEncoder.register(MyClass, lambda x: str(id(x)))
        >>> json.dumps(MyClass)
        '1577854083720'
    """

    _RegisteredClasses = {}

    @classmethod
    def register(cls, encodeCls, encodeFn):
        """Register a class and how to encode it."""
        cls._RegisteredClasses[encodeCls] = encodeFn

    def default(self, o):
        """Handle serialisation for all registered classes."""
        for cls, fn in self._RegisteredClasses.items():
            if isinstance(o, cls):
                return fn(o)
        return super(CustomEncoder, self).default(o)


def getWindowSettingsPath(windowID):
    """Get a path to the window settings."""
    return os.path.join(tempfile.gettempdir(), 'VFXWindow.{}.json'.format(windowID))


def getWindowSettings(windowID, path=None):
    """Load the window settings, or return empty dict if they don't exist."""
    if path is None:
        path = getWindowSettingsPath(windowID)
    try:
        with open(path, 'r') as f:
            return json.loads(f.read())
    except (IOError, ValueError):
        return {}


def saveWindowSettings(windowID, data, path=None):
    """Save the window settings."""
    if path is None:
        path = getWindowSettingsPath(windowID)
    try:
        with open(path, 'w') as f:
            f.write(json.dumps(data, indent=2, cls=CustomEncoder))
    except IOError:
        return False
    return True
