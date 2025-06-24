"""Set the window class to be specific to whichever program is loaded.

Changes for 2.0:
    - Remove legacy callback methods (currently marked as deprecated)
    - Remove `processEvents` (currently marked as deprecated)
    - Remove `displayMessage` (currently marked as deprecated)
    - Change `setDocked` to `setFloating`, remove docked in favour of floating
    - Revise `setDefault` methods
    - Revise signal handling
    - Change `show` override to `launch`
"""

from __future__ import absolute_import

__all__ = ['VFXWindow']
__version__ = '1.10.0'

import os
import sys
import warnings

import Qt

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
        It will crash if this is not run before creating a widget.
    Gaffer:
        Required to launch widgets when running in batch mode.
    """
    from Qt import QtWidgets
    try:
        QtWidgets.QApplication(sys.argv)
    except RuntimeError:
        pass


def _bypassPySide6WebEngine():
    """Blender 4.2.0 has a crash on import on Windows machines.
    Bypassing the QWebEngine components solves it.
    It appears to be solved as of 4.2.1.
    https://community.shotgridsoftware.com/t/shotgrid-with-tk-blender/17217/11
    """
    # Note: PySide6 support was added in Qt.py 1.4.1
    if not getattr(Qt, 'IsPySide6', False):
        return

    # Override QtWebEngine for both Qt and PySide6
    import PySide6
    class QtWebEngineCore:
        QWebEnginePage = None
        QWebEngineProfile = None
    Qt.QtWebEngineCore = PySide6.QtWebEngineCore = QtWebEngineCore
    Qt.QtWebEngineWidgets = PySide6.QtWebEngineWidgets = None


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
    if application.Blender.version == '4.2.0' and sys.platform == 'win32':
        _bypassPySide6WebEngine()
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

elif application.Natron:
    from .natron.gui import NatronWindow as VFXWindow

elif application.Gaffer:
    _setupQApp()
    from .gaffer.gui import GafferWindow as VFXWindow

elif application.RenderDoc:
    from .renderdoc.gui import RenderDocWindow as VFXWindow

else:
    from .standalone.gui import StandaloneWindow as VFXWindow


if os.environ.get('VFXWIN_DEPRECATION_WARNING') == '1':
    warnings.simplefilter('always', VFXWinDeprecationWarning)
