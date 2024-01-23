from __future__ import absolute_import

try:
    import bpy
except ImportError:
    bpy = None

from .abstract import AbstractApplication, AbstractVersion


class BlenderVersion(AbstractVersion):
    """Blender version data for comparisons."""

    def __init__(self):
        self.versionMajor, self.versionMinor, self.versionPatch = bpy.app.version
        super(BlenderVersion, self).__init__(bpy.app.version_string)

    @property
    def major(self):
        """Get the major version number for Blender."""
        return str(self.versionMajor)

    @property
    def minor(self):
        """Get the minor version number for Blender."""
        return str(self.versionMinor)

    @property
    def patch(self):
        """Get the patch version number for Blender."""
        return str(self.versionPatch)


class BlenderApplication(AbstractApplication):
    """Blender application data."""

    NAME = 'Blender'

    IMPORTS = ['bpy']

    PATHS = [
        r'[bB]lender[_\s][fF]oundation',
        r'[bB]lender[_\s]\d+(?:\.\d+){0,2}',
        r'[bB]lender\.(?:bin|exe)',
    ]

    VERSION = BlenderVersion
