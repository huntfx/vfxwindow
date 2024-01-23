import re
import sys

from .utils import standardiseVersions


class AbstractApplication(object):
    """Application data."""

    NAME = ''  # Name of the application

    IMPORTS = []  # List of program imports to test for

    PATHS = []  # Valid paths of the executable

    VERSION = None  # Subclass of `AbstractVersion`

    def __init__(self):
        self.name = self.NAME
        self.loaded = self.isLoaded()
        self.version = self.VERSION() if self.loaded and self.VERSION is not None else None

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<{} {!r}>'.format(self.name.replace(' ', ''), self.version)

    def __bool__(self):
        """If the application is loaded."""
        return self.loaded
    __nonzero__ = __bool__

    def __contains__(self, other):
        try:
            return other.lower() in self.name.lower()
        except AttributeError:
            return False

    def __eq__(self, other):
        """Case insensitive string comparison."""
        try:
            return self.name.lower() == other.lower()
        except AttributeError:
            return False

    def __ne__(self, other):
        """Case insensitive string comparison."""
        try:
            return self.name.lower() != other.lower()
        except AttributeError:
            return True

    def isLoaded(self):
        """Determine if the application is currently loaded.

        If the modules of a DCC can be imported, then it's likely but
        not 100% confirmed that it is within the software environment
        (an example of this is Maya being able to import `hou`).
        This can be paired with checking for known executable paths.

        Note that the imports are done with both `pkgutil.find_loader`
        and `importlib.util.find_spec`, so a simple `__import__` is
        much cleaner to use in this case.
        """
        if any((re.search(pattern, sys.executable) for pattern in self.PATHS)):
            for imp in self.IMPORTS:
                if imp in sys.modules:
                    return True

                try:
                    if __import__(imp):
                        return True
                except ImportError:
                    pass
        return False

    @property
    def gui(self):
        """If the application is in GUI mode."""
        raise True

    @property
    def batch(self):
        """If the application is in batch mode."""
        return not self.gui

    def lower(self):
        """Get the lowercase application name."""
        return self.name.lower()

    def upper(self):
        """Get the uppercase application name."""
        return self.name.upper()


class AbstractVersion(object):
    """Application version data for comparisons."""

    def __init__(self, version):
        self.version = str(version)

    def __repr__(self):
        return repr(self.version)

    def __str__(self):
        """Get the full version number."""
        return self.version

    def __int__(self):
        """Get the major version number."""
        return int(self.version.split('.')[0])

    def __float__(self):
        """Get the major and minor version number."""
        return float('.'.join(self.version.split('.')[:2]))

    def __eq__(self, other):
        """Determine if two versions are equal."""
        a, b = standardiseVersions(self.version, other)
        return a == b

    def __ne__(self, other):
        """Determine if two versions are not equal."""
        a, b = standardiseVersions(self.version, other)
        return a != b

    def __gt__(self, other):
        """Determine if the current version is higher."""
        a, b = standardiseVersions(self.version, other)
        return a > b

    def __ge__(self, other):
        """Determine if the current version is higher or equal."""
        a, b = standardiseVersions(self.version, other)
        return a >= b

    def __lt__(self, other):
        """Determine if the current version is lower."""
        a, b = standardiseVersions(self.version, other)
        return a < b

    def __le__(self, other):
        """Determine if the current version is lower or equal."""
        a, b = standardiseVersions(self.version, other)
        return a <= b

    def __iter__(self):
        """Iterate over the major/minor/patch numbers."""
        return iter(self.split())

    def __getitem__(self, item):
        """Get the major/minor/patch number from an index."""
        return self.split()[item]

    @property
    def major(self):
        """Get the major version number."""
        return self.split()[0]

    @property
    def minor(self):
        """Get the minor version number.
        Returns `None` if not applicable.
        """
        try:
            return self.split()[1]
        except IndexError:
            return None

    @property
    def patch(self):
        """Get the patch version number.
        Returns `None` if not applicable.
        """
        try:
            return self.split()[2]
        except IndexError:
            return None

    def split(self):
        """Get all the version parts."""
        return self.version.split('.')
