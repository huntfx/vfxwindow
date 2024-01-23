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
        version = path.split(os.path.sep)[-2].split(' ', 1)[1]
        super(FusionVersion, self).__init__(version, major=version, minor='0', patch='0')


class FusionApplication(AbstractApplication):
    """Fusion application data."""

    NAME = 'Fusion'

    IMPORTS = ['BlackmagicFusion']

    PATHS = [
        r'^(?:\\|/)Blackmagic Design(?:\\|/)(?:[fF]usion|fuscript)\.(?:bin|exe|app)$',
        r'(?:[fF]usion|fuscript)\.(?:bin|exe|app)$',
    ]

    VERSION = FusionVersion
