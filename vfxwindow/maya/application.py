from __future__ import absolute_import

try:
    import maya.cmds as mc
except ImportError:
    mc = None

from ..abstract.application import AbstractApplication, AbstractVersion


class MayaVersion(AbstractVersion):
    """Maya version data for comparisons."""

    def __init__(self):
        super(MayaVersion, self).__init__(major=mc.about(majorVersion=True),  # '2020'
                                          minor=mc.about(minorVersion=True),  # '4'
                                          patch=mc.about(patchVersion=True))  # '0'


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


Application = MayaApplication()
