from __future__ import absolute_import

import os
import sys

from .abstract import AbstractApplication, AbstractVersion


class MaxVersion(AbstractVersion):
    """3ds Max version data for comparisons."""

    def __init__(self):
        version = sys.executable.split(os.path.sep)[-2].split('_')[-1]
        super(MaxVersion, self).__init__(version, major=version, minor='0', patch='0')


class MaxApplication(AbstractApplication):
    """3ds Max application data."""

    NAME = '3ds Max'

    IMPORTS = ['MaxPlus']

    PATHS = [
        r'3ds[mM]ax\.(?:bin|exe|app)',
    ]

    VERSION = MaxVersion
