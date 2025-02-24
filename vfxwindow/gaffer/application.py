from __future__ import absolute_import

try:
    import Gaffer
    import GafferUI
except ImportError:
    Gaffer = None

from ..abstract.application import AbstractApplication, AbstractVersion


class GafferVersion(AbstractVersion):
    """Gaffer version data for comparisons.

    It does not use true semantic versioning as it includes a milestone
    version too. For the sake of simplicity, the milestone version is
    being set as the major version, the major as minor, etc.
    """

    def __init__(self):
        super(GafferVersion, self).__init__(Gaffer.About.versionString(),
                                            Gaffer.About.milestoneVersion(),
                                            Gaffer.About.majorVersion(),
                                            Gaffer.About.minorVersion(),
                                            Gaffer.About.patchVersion())


class GafferApplication(AbstractApplication):
    """Gaffer application data."""

    NAME = 'Gaffer'

    IMPORTS = ['Gaffer']

    PATHS = [
        '[gG]affer'
    ]

    VERSION = GafferVersion

    @property
    def gui(self):
        """Determine if running in interactive mode."""
        return GafferUI.EventLoop.mainEventLoop().running()


Application = GafferApplication()
