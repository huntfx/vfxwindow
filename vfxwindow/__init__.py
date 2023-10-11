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
__version__ = '1.7.1'

import sys
from .utils import vfxSoftware
from .utils import vfxExceptions


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


if vfxSoftware.isMayaBatch():
    _setup_qapp()
    from .maya import MayaBatchWindow as VFXWindow

elif vfxSoftware.isMaya():
    from .maya import MayaWindow as VFXWindow

elif vfxSoftware.isNuke():
    from .nuke import runningInTerminal

    inTerminal = runningInTerminal(startup=True)
    if inTerminal is None:
        raise vfxExceptions.NotImplementedApplicationError('Nuke GUI not supported in terminal mode, launch nuke with the --tg flag instead.')

    if inTerminal:
        from .nuke import NukeBatchWindow as VFXWindow
    else:
        from .nuke import NukeWindow as VFXWindow

elif vfxSoftware.isHoudini():
    from .houdini import HoudiniWindow as VFXWindow

elif vfxSoftware.isBlender():
    from .blender import BlenderWindow as VFXWindow

elif vfxSoftware.isUnrealEngine():
    from .unreal import UnrealWindow as VFXWindow

elif vfxSoftware.is3dsMax():
    from .max import MaxWindow as VFXWindow

elif vfxSoftware.isSubstanceDesigner():
    from .substance_designer import SubstanceDesignerWindow as VFXWindow

elif vfxSoftware.isSubstancePainter():
    VFXWindow = substance_painter.SubstancePainterWindow

elif vfxSoftware.isFusion360():
    from .fusion import FusionWindow as VFXWindow

else:
    from .standalone import StandaloneWindow as VFXWindow
