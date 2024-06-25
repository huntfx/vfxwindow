from __future__ import absolute_import

try:
    import renderdoc as rd
except ImportError:
    rd = None

from ..abstract.application import AbstractApplication, AbstractVersion


class RenderDocVersion(AbstractVersion):
    """RenderDoc version data for comparisons."""

    def __init__(self):
        super(RenderDocVersion, self).__init__(rd.GetVersionString())  # '1.33'


class RenderDocApplication(AbstractApplication):
    """RenderDoc application data."""

    NAME = 'RenderDoc'

    IMPORTS = ['renderdoc', 'qrenderdoc']

    PATHS = [
        r'(?:\\|/)RenderDoc(?:\\|/)qrenderdoc\.(?:bin|exe|app)$',
    ]

    VERSION = RenderDocVersion


Application = RenderDocApplication()
