from __future__ import absolute_import

try:
    import maya.cmds as mc
except ImportError:
    mc = None

from .abstract import AbstractApplication, AbstractVersion


class MayaVersion(AbstractVersion):
    """Maya version data for comparisons."""

    def __init__(self):
        self.versionMajor = mc.about(majorVersion=True)  # '2020'
        self.versionMinor = mc.about(minorVersion=True)  # '4'
        self.versionPatch = mc.about(patchVersion=True)  # '0'
        version = '{}.{}.{}'.format(self.versionMajor, self.versionMinor, self.versionPatch)
        super(MayaVersion, self).__init__(version)

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


class MayaApplication(AbstractApplication):
    """Maya application data."""

    NAME = 'Maya'

    IMPORTS = ['maya.cmds']

    PATHS = [
        # GUI
        r'^[A-Z]:\\Program\sFiles(?:|\s\(x86\))\\[aA]utodesk\\[mM]aya\d{4}\\bin\\[mM]aya\.exe$',  # Windows
        r'^/usr/[aA]utodesk/[mM]aya(?:\d{4})?/bin/[mM]aya\.bin$',  # Linux
        r'^/Applications/[mM]aya\s\d{4}/[mM]aya\.app$',  # MacOs
        r'^.*(?:\\|/)bin(?:\\|/)[mM]aya\.(?:bin|exe|app)$',  # Common
        r'^.*(?:\\|/)[mM]aya\.(?:bin|exe|app)$',  # Common

        # Batch
        r'^[A-Z]:\\Program\sFiles(?:|\s\(x86\))\\[aA]utodesk\\[mM]aya\d{4}\\(?:bin|bin2|bin\\\.\.\\bin2)\\[mM]ayapy[2]?\.exe$',  # Windows
        r'^/usr/[aA]utodesk/[mM]aya\d{4}/(?:bin|bin2|bin/\.\./bin2)/[pP]ython-bin$',  # Linux
        r'[mM]ayapy\.(?:bin|exe|app)',  # Common
    ]

    VERSION = MayaVersion

    @property
    def gui(self):
        """If Maya is in GUI mode."""
        return not mc.about(batch=True)

    @property
    def batch(self):
        """If Maya is in batch mode."""
        return mc.about(batch=True)
