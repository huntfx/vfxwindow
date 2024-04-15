"""Set the window class to be specific to whichever program is loaded.

TODO:
    Substance callbacks
    Add dialog code for each application
    Revise setDefault* methods

    # Potential breaking changes
    Change setDocked to setFloating
    Remove docked in favour of floating
    Changed dialog to isDialog
    Remove processEvents
    Remove signalExists
"""

from __future__ import absolute_import

__all__ = ['VFXWindow']
__version__ = '1.9.0'

import sys
from . import application


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


if application.Maya:
    if application.Maya.batch:
        _setup_qapp()
        from .maya.gui import MayaBatchWindow as VFXWindow
    else:
        from .maya.gui import MayaWindow as VFXWindow

elif application.Nuke:
    if application.Nuke.batch:
        from .nuke.gui import NukeBatchWindow as VFXWindow
    else:
        from .nuke.gui import NukeWindow as VFXWindow

elif application.Houdini:
    from .houdini.gui import HoudiniWindow as VFXWindow

elif application.Blender:
    from .blender.gui import BlenderWindow as VFXWindow

elif application.Unreal:
    from .unreal.gui import UnrealWindow as VFXWindow

elif application.Max:
    from .max.gui import MaxWindow as VFXWindow

elif application.SubstanceDesigner:
    from .substance_designer.gui import SubstanceDesignerWindow as VFXWindow

elif application.SubstancePainter:
    from .substance_painter.gui import SubstancePainterWindow as VFXWindow

elif application.Fusion:
    from .fusion.gui import FusionWindow as VFXWindow

elif application.CryEngine:
    from .cryengine.gui import CryWindow as VFXWindow

else:
    from .standalone.gui import StandaloneWindow as VFXWindow
