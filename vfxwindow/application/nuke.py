from __future__ import absolute_import

from Qt import QtWidgets

try:
    import nuke
except ImportError:
    nuke = None

from .abstract import AbstractApplication, AbstractVersion
from ..exceptions import NotImplementedApplicationError


class NukeVersion(AbstractVersion):
    """Nuke version data for comparisons."""

    def __init__(self):
        self.versionMajor = nuke.NUKE_VERSION_MAJOR  # 12
        self.versionMinor = nuke.NUKE_VERSION_MINOR  # 1
        self.versionPatch = nuke.NUKE_VERSION_RELEASE  # 3
        super(NukeVersion, self).__init__(nuke.NUKE_VERSION_STRING)  # '12.1v3'

    @property
    def major(self):
        """Get the major version number for Nuke."""
        return str(self.versionMajor)

    @property
    def minor(self):
        """Get the minor version number for Nuke."""
        return str(self.versionMinor)

    @property
    def patch(self):
        """Get the patch version number for Nuke."""
        return str(self.versionPatch)


class NukeApplication(AbstractApplication):
    """Nuke application data."""

    NAME = 'Nuke'

    IMPORTS = ['nuke']

    PATHS = [
        r'[nN]uke\d+(?:\.\d+){0,2}\.(?:bin|exe|app)',
        r'[nN]uke\.(?:bin|exe|app)',
    ]

    VERSION = NukeVersion

    def __init__(self):
        super(NukeApplication, self).__init__()

        # Check Qt is supported
        if self.loaded and not QtWidgets.QApplication.topLevelWidgets():
            raise NotImplementedApplicationError('Nuke GUI not supported in terminal mode, launch nuke with the --tg flag instead.')

    @property
    def gui(self):
        """Determine if Nuke is in GUI mode."""
        return nuke.GUI
