from __future__ import absolute_import

import os
import sys

from ..abstract.application import AbstractApplication, AbstractVersion


class CryEngineVersion(AbstractVersion):
    """CryEngine Sandbox version data for comparisons."""

    def __init__(self):
        # TODO: Check what path was
        try:
            version = sys.executable.split(os.path.sep)[-4].rsplit('.', 1)[0]
        except (TypeError, IndexError):
            version = ''
        super(CryEngineVersion, self).__init__(version)


class CryEngineApplication(AbstractApplication):
    """CryEngine Sandbox application data."""

    NAME = 'CryEngine Sandbox'

    IMPORTS = ['SandboxBridge']

    PATHS = [
        r'[sS]andbox\.(?:bin|exe|app)$',
    ]

    VERSION = CryEngineVersion


Application = CryEngineApplication()
