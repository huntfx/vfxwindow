from __future__ import absolute_import

try:
    import hou
except ImportError:
    hou = None

from ..abstract.application import AbstractApplication, AbstractVersion


class HoudiniVersion(AbstractVersion):
    """Houdini version data for comparisons."""

    def __init__(self):
        super(HoudiniVersion, self).__init__(hou.applicationVersionString(),  # '18.5.488'
                                             *hou.applicationVersion())  # (18, 5, 499)


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

    @property
    def gui(self):
        """If the application is in GUI mode."""
        return hou.isUIAvailable()


Application = HoudiniApplication()
