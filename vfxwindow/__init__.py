"""Set the window class to be specific to whichever program is loaded."""

from __future__ import absolute_import

__version__ = '1.2.6'

import os
import sys

# The imports are nested as an easy way to stop importing once a window is found
try:
    import maya.cmds

except ImportError:
    try:
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
                    from .standalone import StandaloneWindow as VFXWindow
                else:
                    from .unreal import UnrealWindow as VFXWindow
            else:
                from .blender import BlenderWindow as VFXWindow
        else:
            from .houdini import HoudiniWindow as VFXWindow
    else:
        from .nuke import NukeWindow as VFXWindow
else:
    if type(sys.stdout) == file:
        # Attempt to start a QApplication automatically if Maya is in batch mode
        # Important: This MUST happen before pymel.core is imported
        from .utils.Qt import QtWidgets
        try:
            app = QtWidgets.QApplication(sys.argv)
        except RuntimeError:
            pass
        from .maya import MayaBatchWindow as VFXWindow
    else:
        from .maya import MayaWindow as VFXWindow
