from __future__ import absolute_import

import os
import sys

from .abstract import AbstractApplication, AbstractVersion


class UnrealVersion(AbstractVersion):
    """Unreal version data for comparisons."""

    def __init__(self):
        path = sys.executable  # C:\Program Files\Epic Games\UE_5.3\Engine\Binaries\Win64\UnrealEditor.exe
        version = path.split(os.path.sep)[-5].split('_')[1]
        self.versionMajor, self.versionMinor = version.split('.')
        super(UnrealVersion, self).__init__(version)

    @property
    def major(self):
        """Get the major version number for Unreal."""
        return self.versionMajor

    @property
    def minor(self):
        """Get the minor version number for Unreal."""
        return self.versionMinor

    @property
    def patch(self):
        """Get the patch version number for Unreal."""
        return '0'


class UnrealApplication(AbstractApplication):
    """Unreal application data."""

    NAME = 'Unreal Engine'

    IMPORTS = ['unreal']

    PATHS = [
        r'[uU]nreal[eE](?:ngine|ditor)\.(?:bin|exe)',
        r'.*?_[uU]nreal_[eE]ngine_\d+\.\d+\.\d+',
        r'[uU]nreal[eE](?:ngine|ditor)',
        r'(?:ue|UE)\d+[eE]ditor',
    ]

    VERSION = UnrealVersion
