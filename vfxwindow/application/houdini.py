from __future__ import absolute_import

try:
    import hou
except ImportError:
    hou = None

from .abstract import AbstractApplication, AbstractVersion


class HoudiniVersion(AbstractVersion):
    """Houdini version data for comparisons."""

    def __init__(self):
        self.versionMajor, self.versionMinor, self.versionPatch = hou.applicationVersion()
        super(HoudiniVersion, self).__init__(hou.applicationVersionString())

    @property
    def major(self):
        """Get the major version number for Houdini."""
        return str(self.versionMajor)

    @property
    def minor(self):
        """Get the minor version number for Houdini."""
        return str(self.versionMinor)

    @property
    def patch(self):
        """Get the patch version number for Houdini."""
        return str(self.versionPatch)


class HoudiniApplication(AbstractApplication):
    """Houdini application data."""

    NAME = 'Houdini'

    IMPORTS = ['hou']

    PATHS = [
        r'[hH]oudini(?:core|fx|)\.(?:bin|exe|app)',  # Windows, MacOS
        r'hfs\d+\.\d+\.\d+',  # Linux
        r'hindie-bin',  # Indie
    ]

    VERSION = HoudiniVersion
