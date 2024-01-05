from __future__ import absolute_import

try:
    import maya.cmds as mc
except ImportError:
    mc = None

from .abstract import AbstractApplication, AbstractVersion



class MayaApplication(AbstractApplication):
    """Maya application data."""

    def __init__(self):
        super(MayaApplication, self).__init__('Maya', MayaVersion() if self.loaded else None)

    @property
    def loaded(self):
        return mc is not None

    @property
    def gui(self):
        """If Maya is in GUI mode."""
        return not mc.about(batch=True)

    @property
    def batch(self):
        """If Maya is in batch mode."""
        return mc.about(batch=True)


class MayaVersion(AbstractVersion):
    """Maya version data for comparisons."""

    def __init__(self):
        self.versionMajor = mc.about(majorVersion=True)
        self.versionMinor = mc.about(minorVersion=True)
        self.versionPatch = mc.about(patchVersion=True)
        version = '{}.{}.{}'.format(self.versionMajor, self.versionMinor, self.versionPatch)
        super(MayaVersion, self).__init__(version)

    def __bool__(self):
        """Determine if Maya is loaded."""
        return mc is not None

    @property
    def major(self):
        """Get the major version number for Maya."""
        return str(self.versionMajor)

    @property
    def minor(self):
        """Get the minor version number for Maya."""
        return str(self.versionMinor)

    @property
    def patch(self):
        """Get the patch version number for Maya."""
        return str(self.versionPatch)
