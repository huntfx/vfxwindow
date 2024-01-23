from __future__ import absolute_import

import os

try:
    import BlackmagicFusion as bmd
except ImportError:
    bmd = None

from .abstract import AbstractApplication, AbstractVersion


class FusionVersion(AbstractVersion):
    """Fusion version data for comparisons."""

    def __init__(self):
        path = bmd.getcurrentdir()  # C:\Program Files\Blackmagic Design\Fusion 9\
        self.versionMajor = path.split(os.path.sep)[-2].split(' ', 1)[1]
        super(FusionVersion, self).__init__(self.versionMajor)

    @property
    def major(self):
        """Get the major version number for Fusion."""
        return str(self.versionMajor)

    @property
    def minor(self):
        """Get the minor version number for Fusion."""
        return None

    @property
    def patch(self):
        """Get the patch version number for Fusion."""
        return None


class FusionApplication(AbstractApplication):
    """Fusion application data."""

    NAME = 'Fusion'

    IMPORTS = ['BlackmagicFusion']

    PATHS = [
        r'^(?:\\|/)Blackmagic Design(?:\\|/)(?:[fF]usion|fuscript)\.(?:bin|exe|app)$',
        r'(?:[fF]usion|fuscript)\.(?:bin|exe|app)$',
    ]

    VERSION = FusionVersion
