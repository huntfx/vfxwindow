"""Set the window class to be specific to whichever program is loaded.

TODO:
    Substance callbacks
    Add dialog code for each application
    Revise setDefault* methods

    # Potential breaking changes
    Change setDocked to setFloating
    Remove docked in favour of floating
    Remove *_VERSION constants
    Changed dialog to isDialog
    Remove processEvents
    Remove signalExists
"""

from __future__ import absolute_import

__all__ = ['VFXWindow']
__version__ = '1.6.4'

import os
import sys
try:
    from importlib.util import find_spec as _importable
except ImportError:
    from pkgutil import find_loader as _importable


def _setup_qapp():
    """Attempt to start a QApplication automatically in batch mode.
    The purpose of this is to override whatever the program uses.
    This must happen before any libraries are imported, as it's usually
    at that point when the QApplication is initialised.
    """

    from Qt import QtWidgets
    try:
        app = QtWidgets.QApplication(sys.argv)
    except RuntimeError:
        pass


def importable(program):
    """Find which imports can be performed.
    In rare circumstances a TypeError can be raised, but it's safe to
    ignore and assume it's not the correct program.
    """

    try:
        return bool(_importable(program))
    except TypeError:
        return None


class NotImplementedApplicationError(ImportError, NotImplementedError):
    """Basically acts as a NotImplementedError, but "except ImportError" will catch it."""


if importable('maya') and 'mayapy.exe' in sys.executable:
    _setup_qapp()
    from .maya import MayaBatchWindow as VFXWindow

elif importable('maya') and 'maya.exe' in sys.executable:
    from .maya import MayaWindow as VFXWindow

elif importable('nuke') and 'Nuke' in sys.executable:
    if False and type(sys.stdout) == file:  # This check doesn't seem to work for Nuke 12
        raise NotImplementedApplicationError('unable to use qt when nuke is in batch mode')
        from .nuke import NukeBatchWindow as VFXWindow
    else:
        from .nuke import NukeWindow as VFXWindow

elif importable('hou') and 'houdini' in sys.executable:
    from .houdini import HoudiniWindow as VFXWindow

elif importable('bpy') and 'Blender Foundation' in sys.executable:
    from .blender import BlenderWindow as VFXWindow

elif importable('unreal') and 'UE4Editor.exe' in sys.executable:
    from .unreal import UnrealWindow as VFXWindow

elif importable('MaxPlus') and '3dsmax.exe' in sys.executable:
    from .max import MaxWindow as VFXWindow

elif importable('sd') and 'Substance Designer.exe' in sys.executable:
    from .substance import SubstanceWindow as VFXWindow

elif importable('fusionscript') or importable('PeyeonScript') and 'Fusion.exe' in sys.executable:
    from .fusion import FusionWindow as VFXWindow

else:
    from .standalone import StandaloneWindow as VFXWindow
