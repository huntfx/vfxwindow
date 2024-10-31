from __future__ import absolute_import

try:
    import NatronEngine
except ImportError:
    natron = None

from ..abstract.application import AbstractApplication, AbstractVersion


class NatronVersion(AbstractVersion):
    """Natron version data for comparisons."""

    def __init__(self):
        super(NatronVersion, self).__init__(NatronEngine.natron.getNatronVersionString(),  # 2.5
                                            major=NatronEngine.natron.getNatronVersionMajor(),  # 2
                                            minor=NatronEngine.natron.getNatronVersionMinor(),  # 5
                                            patch=NatronEngine.natron.getNatronVersionRevision())  # 0


class NatronApplication(AbstractApplication):
    """Natron application data."""

    NAME = 'Natron'

    IMPORTS = ['NatronEngine']

    PATHS = [
        r'[nN]atron\.(?:bin|exe|app)',
    ]

    VERSION = NatronVersion


Application = NatronApplication()
