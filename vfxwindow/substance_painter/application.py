from __future__ import absolute_import

try:
    import substance_painter
except ImportError:
    substance_painter = None

from ..abstract.application import AbstractApplication, AbstractVersion


class SubstancePainterVersion(AbstractVersion):
    """Substance Painter version data for comparisons."""

    def __init__(self):
        try:
            args = [substance_painter.application.version()]  # '8.3.0'
            args.extend(substance_painter.application.version_info())  # (8, 3, 0)
        except AttributeError:
            args = [substance_painter.js.evaluate('alg.version.painter')]  # '8.3.0'
        super(SubstancePainterVersion, self).__init__(*args)


class SubstancePainterApplication(AbstractApplication):
    """Substance Painter application data."""

    NAME = 'Substance Painter'

    IMPORTS = ['substance_painter']

    PATHS = [
        r'[pP]ainter\.(?:bin|exe|app)',
        r'[sS]ubstance(?:_|\s)3[dD](?:_|\s)[pP]ainter',
    ]

    VERSION = SubstancePainterVersion


Application = SubstancePainterApplication()
