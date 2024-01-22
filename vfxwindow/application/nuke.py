from __future__ import absolute_import

from Qt import QtWidgets

try:
    import nuke
except ImportError:
    nuke = None

from .abstract import AbstractApplication, AbstractVersion
from ..exceptions import NotImplementedApplicationError


class NukeApplication(AbstractApplication):
    """Nuke application data."""

    def __init__(self):
        super(NukeApplication, self).__init__('Nuke', NukeVersion() if self.loaded else None)

        if self.loaded and not QtWidgets.QApplication.topLevelWidgets():
            raise NotImplementedApplicationError('Nuke GUI not supported in terminal mode, launch nuke with the --tg flag instead.')

    @property
    def loaded(self):
        return nuke is not None

    @property
    def gui(self):
        """Determine if Nuke is in GUI mode."""
        return nuke.GUI


class NukeVersion(AbstractVersion):
    """Nuke version data for comparisons."""

    def __init__(self):
        self.versionMajor = nuke.NUKE_VERSION_MAJOR
        self.versionMinor = nuke.NUKE_VERSION_MINOR
        self.versionPatch = nuke.NUKE_VERSION_RELEASE
        version = nuke.NUKE_VERSION_STRING
        super(NukeVersion, self).__init__(version)

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
