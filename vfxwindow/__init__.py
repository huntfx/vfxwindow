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
__version__ = '1.9.1'

import os
import sys
import warnings

from . import application
from .exceptions import VFXWinDeprecationWarning

# Ensure sys.argv exists
if not hasattr(sys, 'argv'):
    sys.argv = []


def _setupQApp():
    """Attempt to start a QApplication.

    Maya:
        When running in batch mode, if this isn't run first, then it
        will set up its own QApplication that is not compatible with
        GUI elements.
    Blender:
        It will crash if this is not run.
    """
    from Qt import QtWidgets
    try:
        QtWidgets.QApplication(sys.argv)
    except RuntimeError:
        pass


if application.Maya:
    if application.Maya.batch:
        _setupQApp()
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
    from .blender.compatibility import bypassWebEngine
    bypassWebEngine()
    _setupQApp()
    from .blender.gui import BlenderWindow as VFXWindow

elif application.Katana:
    from .katana.gui import KatanaWindow as VFXWindow

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

elif application.RenderDoc:
    from .renderdoc.gui import RenderDocWindow as VFXWindow

else:
    from .standalone.gui import StandaloneWindow as VFXWindow


if os.environ.get('VFXWIN_DEPRECATION_WARNING') == '1':
    warnings.simplefilter('always', VFXWinDeprecationWarning)
