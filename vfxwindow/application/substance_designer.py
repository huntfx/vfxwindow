from __future__ import absolute_import

try:
    import sd
except ImportError:
    sd = None

from .abstract import AbstractApplication, AbstractVersion


class SubstanceDesignerVersion(AbstractVersion):
    """Substance Designer version data for comparisons."""

    def __init__(self):
        app = sd.getContext().getSDApplication()
        super(SubstanceDesignerVersion, self).__init__(app.getVersion())  # '12.3.1'


class SubstanceDesignerApplication(AbstractApplication):
    """Substance Designer application data."""

    NAME = 'Substance Designer'

    IMPORTS = ['sd']

    PATHS = [
        r'[dD]esigner\.(?:bin|exe|app)',
        r'[sS]ubstance(?:_|\s)3[dD](?:_|\s)[dD]esigner',
    ]

    VERSION = SubstanceDesignerVersion
