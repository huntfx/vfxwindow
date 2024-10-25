from __future__ import absolute_import

try:
    import nuke
except ImportError:
    nuke = None

from ..abstract.application import AbstractApplication, AbstractVersion


class NukeVersion(AbstractVersion):
    """Nuke version data for comparisons."""

    def __init__(self):
        super(NukeVersion, self).__init__(nuke.NUKE_VERSION_STRING,  # '12.1v3'
                                          major=nuke.NUKE_VERSION_MAJOR,  # 12
                                          minor=nuke.NUKE_VERSION_MINOR,  # 1
                                          patch=nuke.NUKE_VERSION_RELEASE)  # 3


class NukeApplication(AbstractApplication):
    """Nuke application data."""

    NAME = 'Nuke'

    IMPORTS = ['nuke']

    PATHS = [
        r'[nN]uke\d+(?:\.\d+){0,2}\.(?:bin|exe|app)',
        r'[nN]uke\.(?:bin|exe|app)',
    ]

    VERSION = NukeVersion

    @property
    def gui(self):
        """Determine if Nuke is in GUI mode."""
        return nuke.GUI


Application = NukeApplication()
