from __future__ import absolute_import

import inspect
import os
import site
import sys
from functools import wraps
from types import ModuleType
from Qt import QtWidgets

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
    # Read the globals from the module at the top of the stack
    if globalsDict is None:
        globalsDict = inspect.stack()[-1][0].f_globals

    # Initially mark every builtin module as visisted
    if visited is None:
        visited = set(filter(bool, map(sys.modules.get, sys.builtin_module_names)))

    for k, v in globalsDict.items():
        if v == cls:
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

            # Recursively search the next module
            result = searchGlobals(cls, v.__dict__, visited=visited)
            if result:
                return k + '.' + result


def forceMenuBar(win):
    """Force add the menuBar if it is not there by default.
    In Maya this is needed for docked windows.

    Each menuBar appears to contain a QToolButton and then the menus,
    so check how many children
    This only works with .insertWidget() - creating a new layout and
    adding both widgets won't do anything.
    """
    menu = win.menuBar()
    for child in menu.children():
        if isinstance(child, QtWidgets.QMenu):
            break
    else:
        return
    menu.setSizePolicy(menu.sizePolicy().horizontalPolicy(), QtWidgets.QSizePolicy.Fixed)
    win.centralWidget().layout().insertWidget(0, menu)
