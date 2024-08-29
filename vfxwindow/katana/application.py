from __future__ import absolute_import

import os

try:
    from Katana import Configuration
except ImportError:
    Configuration = None

from ..abstract.application import AbstractApplication, AbstractVersion


class KatanaVersion(AbstractVersion):
    """Katana version data for comparisons."""

    def __init__(self):
        super(KatanaVersion, self).__init__(os.environ['KATANA_RELEASE'])  # 7.1v3


class KatanaApplication(AbstractApplication):
    """Katana application data."""

    NAME = 'Katana'

    IMPORTS = ['Katana']

    PATHS = [
        r'[kK]atana.*python\.(?:bin|exe|app)',
    ]

    VERSION = KatanaVersion

    @property
    def gui(self):
        """If Katana is in UI mode."""
        if Configuration is None:
            raise RuntimeError('katana not running')
        return bool(Configuration.get('KATANA_UI_MODE'))

    @property
    def batch(self):
        """If Katana is in batch mode."""
        if Configuration is None:
            raise RuntimeError('katana not running')
        return bool(Configuration.get('KATANA_BATCH_MODE'))


Application = KatanaApplication()
