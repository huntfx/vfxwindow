import re
import sys

from .utils import standardiseVersions


def _toCamelCase(string):
    """Convert the application name to camel case.

    Source: https://stackoverflow.com/a/20744956
    """
    output = ''.join(x for x in string.title() if x.isalnum())
    return output[0].lower() + output[1:]


class AbstractApplication(str):
    """Application data.

    Note that the string representation the user sees is a title, and
    the equality checks work with this. Interally it is camel case so
    that dictionary keys may work with it smoothly.
    """

    NAME = ''  # Name of the application

    IMPORTS = []  # List of program imports to test for

    PATHS = []  # Valid paths of the executable

    VERSION = None  # Subclass of `AbstractVersion`

    def __new__(cls):
        new = str.__new__(cls, _toCamelCase(cls.NAME))
        new.name = cls.NAME
        new.loaded = cls.isLoaded()
        new.version = cls.VERSION() if new.loaded and cls.VERSION is not None else None
        return new

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
        name = self.name.lower()
        try:
            other = other.lower()
        except AttributeError:
            return False

        if name == other:
            return True

        if ' ' in name:
            # Check if name contains a part ('3ds Max' == 'Max')
            if any(part in other for part in name.split(' ')):
                return True
            # Check if mismatched spaces ('3ds Max' == '3dsmax')
            if name.replace(' ', '') == other.replace(' ', ''):
                return True

        return False

    def __ne__(self, other):
        """Case insensitive string comparison."""
        return not self.__eq__(other)

    @classmethod
    def isLoaded(cls):
        """Determine if the application is currently loaded.

        If the modules of a DCC can be imported, then it's likely but
        not 100% confirmed that it is within the software environment
        (an example of this is Maya being able to import `hou`).
        This can be paired with checking for known executable paths.

        Note that the imports are done with both `pkgutil.find_loader`
        and `importlib.util.find_spec`, so a simple `__import__` is
        much cleaner to use in this case.
        """
        if any((re.search(pattern, sys.executable) for pattern in cls.PATHS)):
            for imp in cls.IMPORTS:
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


class AbstractVersion(object):
    """Application version data for comparisons."""

    def __init__(self, version=None, major=None, minor=None, patch=None):
        parts = (major, minor, patch)

        # Build the version string
        if not version:
            validParts = []
            for num in parts:
                if num is None:
                    break
                validParts.append(num)
            version = '.'.join(validParts)
        self.version = str(version)

        # Split to major/minor/patch
        if major is not None:
            major = str(major)
        if minor is not None:
            minor = str(minor)
        if patch is not None:
            patch = str(patch)

        self.major = major
        self.minor = minor
        self.patch = patch

        if None in parts:
            split = version.split('.')
            if self.major is None:
                try:
                    self.major = split[0]
                except IndexError:
                    self.major = '0'
            if self.minor is None:
                try:
                    self.minor = split[1]
                except IndexError:
                    self.minor = '0'
            if self.patch is None:
                try:
                    self.patch = split[2]
                except IndexError:
                    self.patch = '0'

    def __repr__(self):
        return repr(self.version)

    def __str__(self):
        """Get the full version number."""
        return self.version

    def __int__(self):
        """Get the major version number."""
        if not self.version:
            return 0
        return int(self.major)

    def __float__(self):
        """Get the major and minor version number."""
        if not self.version:
            return 0.0
        return float(self.major + '.' + self.minor)

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

    def __getitem__(self, item):
        """Get the major/minor/patch number from an index."""
        return (self.major, self.minor, self.patch)[item]

    def split(self, sep='.'):
        """Get all the version parts."""
        return self.version.split(sep)
