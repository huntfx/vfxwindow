from __future__ import absolute_import

try:
    import bpy
except ImportError:
    bpy = None

from ..abstract.application import AbstractApplication, AbstractVersion


class BlenderVersion(AbstractVersion):
    """Blender version data for comparisons."""

    def __init__(self):
        super(BlenderVersion, self).__init__(None, *bpy.app.version)  # (3, 6, 0)


class BlenderApplication(AbstractApplication):
    """Blender application data."""

    NAME = 'Blender'

    IMPORTS = ['bpy']

    PATHS = [
        r'[bB]lender[_\s][fF]oundation',
        r'[bB]lender[_\s-]\d+(?:\.\d+){0,2}',
        r'[bB]lender\.(?:bin|exe)',
    ]

    VERSION = BlenderVersion

    def gui(self):
        if bpy is None:
            return True
        return not bpy.app.background


Application = BlenderApplication()
