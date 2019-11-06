"""Set the window class to be specific to whichever program is loaded."""

from __future__ import absolute_import

__version__ = '1.2.3'

import os

# The imports are nested as an easy way to stop importing once a window is found
try:
    import maya.cmds as cmds

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
    from .maya import MayaWindow as VFXWindow
    