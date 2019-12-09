"""Set the window class to be specific to whichever program is loaded."""

from __future__ import absolute_import

__version__ = '1.3.0'

import os
import sys


def _setup_qapp():
    """Attempt to start a QApplication automatically in batch mode.
    The purpose of this is to override whatever the program uses.
    This must happen before any libraries are imported, as it's usually
    at that point when the QApplication is initialised.
    """
    from .utils.Qt import QtWidgets
    try:
        app = QtWidgets.QApplication(sys.argv)
    except RuntimeError:
        pass


# The imports are nested as an easy way to stop importing once a window is found
try:
    import maya.cmds

except ImportError:
    try:
        if os.path.sep+'Nuke' in sys.executable and type(sys.stdout) == file:
            _setup_qapp()
        import nuke
        import nukescripts

    except ImportError:
        try:
            import hou
            hou.qt  # The hou module works outside of Houdini, so also check for qt

        except (ImportError, AttributeError):
            try:
                import bpy
            except ImportError:
                try:
                    import unreal
                except ImportError:
                    try:
                        import MaxPlus
                    except ImportError:
                        from .standalone import StandaloneWindow as VFXWindow
                    else:
                        from .max import MaxWindow as VFXWindow
                else:
                    from .unreal import UnrealWindow as VFXWindow
            else:
                from .blender import BlenderWindow as VFXWindow
        else:
            from .houdini import HoudiniWindow as VFXWindow
    else:
        if type(sys.stdout) == file:
            from .nuke import NukeBatchWindow as VFXWindow
        else:
            from .nuke import NukeWindow as VFXWindow
else:
    if type(sys.stdout) == file:
        _setup_qapp()
        from .maya import MayaBatchWindow as VFXWindow
    else:
        from .maya import MayaWindow as VFXWindow
