from __future__ import absolute_import

import os
import sys

from .abstract import AbstractApplication, AbstractVersion


class MaxVersion(AbstractVersion):
    """3ds Max version data for comparisons."""

    def __init__(self):
        self.versionMajor = sys.executable.split(os.path.sep)[-2][8:]
        super(MaxVersion, self).__init__(self.versionMajor)

    @property
    def major(self):
        """Get the major version number for 3ds Max."""
        return self.versionMajor

    @property
    def minor(self):
        """Get the minor version number for 3ds Max."""
        return '0'

    @property
    def patch(self):
        """Get the patch version number for 3ds Max."""
        return '0'


class MaxApplication(AbstractApplication):
    """3ds Max application data."""

    NAME = '3ds Max'

    IMPORTS = ['MaxPlus']

    PATHS = [
        r'3ds[mM]ax\.(?:bin|exe|app)',
    ]

    VERSION = MaxVersion
