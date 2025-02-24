"""Base classes for applications and versions.

The following applications are not currently implemented:
Mari:
    Module: mari
    [mM]ari\d+(?:\.\d+){0,2}\.(?:bin|exe|app)
    [mM]ari\.(?:bin|exe|app)
Modo:
    Module: lx
    [mM]odo\d+(?:\.\d+){0,2}\.(?:bin|exe|app)
    [mM]odo\.(?:bin|exe|app)
Hiero:
    Module: hiero
    [hH]iero\d+(?:\.\d+){0,2}\.(?:bin|exe|app)
    [hH]iero\.(?:bin|exe|app)
Motion Builder:
    Module: pyfbsdk, pyfbsdk_additions
    ^.*(?:\\|/)[mM]otion[bB]uilder\d{4}(?:\\|/)[mM]otion[bB]uilder\.(?:bin|exe|app)
    [mM]otion[bB]uilder\.(?:bin|exe|app)
"""

import re
import sys

from ..utils import CustomEncoder
from ..utils.application import standardiseVersions


class AbstractApplication(str):
    """Application data."""

    NAME = ''  # Name of the application

    IMPORTS = []  # List of program imports to test for

    PATHS = []  # Valid paths of the executable

    VERSION = None  # Subclass of `AbstractVersion`

    def __new__(cls):
        new = str.__new__(cls, cls.NAME)
        new.name = cls.NAME
        new.loaded = cls.isLoaded()
        if cls.VERSION is None or not new.loaded:
            new.version = None
        else:
            new.version = cls.VERSION()
        return new

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
            if ' ' not in other and any(part in other for part in name.split(' ')):
                return True
            # Check if mismatched spaces ('3ds Max' == '3dsmax')
            if name.replace(' ', '') == other.replace(' ', ''):
                return True

        return False

    def __ne__(self, other):
        """Case insensitive string comparison."""
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)

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
        return True

    @property
    def batch(self):
        """If the application is in batch mode."""
        return not self.gui


class AbstractVersion(object):
    """Application version data for comparisons."""

    def __init__(self, version=None, major=None, minor=None, patch=None, *extra):
        if major is not None:
            major = str(major)
        if minor is not None:
            minor = str(minor)
        if patch is not None:
            patch = str(patch)
        parts = (major, minor, patch)

        # Generate the version string from the parts
        if not version:
            validParts = []
            for num in parts:
                if num is None:
                    break
                validParts.append(num)
            version = '.'.join(validParts + list(extra))

        # Get any missing parts from the version string
        if None in parts:
            split = version.replace('v', '.').split('.')
            if major is None:
                try:
                    major = split[0]
                except IndexError:
                    major = '0'
            if minor is None:
                try:
                    minor = split[1]
                except IndexError:
                    minor = '0'
            if patch is None:
                try:
                    patch = split[2]
                except IndexError:
                    patch = '0'

        self.version = str(version)
        self.major = major
        self.minor = minor
        self.patch = patch
        self.extra = extra

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
        return self.split()[item]

    def split(self, sep='.'):
        """Get all the version parts."""
        return self.version.split(sep)


CustomEncoder.register(AbstractApplication, str)
