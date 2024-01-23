from __future__ import absolute_import

try:
    import substance_painter
except ImportError:
    substance_painter = None

from .abstract import AbstractApplication, AbstractVersion


class SubstancePainterVersion(AbstractVersion):
    """Substance Painter version data for comparisons."""

    def __init__(self):
        version = substance_painter.js.evaluate('alg.version.painter')  # '8.3.0'
        super(SubstancePainterVersion, self).__init__(version)


class SubstancePainterApplication(AbstractApplication):
    """Substance Painter application data."""

    NAME = 'Substance Painter'

    IMPORTS = ['substance_painter']

    PATHS = [
        r'[pP]ainter\.(?:bin|exe|app)',
        r'[sS]ubstance(?:_|\s)3[dD](?:_|\s)[pP]ainter',
    ]

    VERSION = SubstancePainterVersion
