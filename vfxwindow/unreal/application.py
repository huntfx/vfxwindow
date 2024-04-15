from __future__ import absolute_import

import os
import sys

from ..abstract.application import AbstractApplication, AbstractVersion


class UnrealVersion(AbstractVersion):
    """Unreal version data for comparisons."""

    def __init__(self):
        version = sys.executable.split(os.path.sep)[-5].split('_')[1]  # C:\Program Files\Epic Games\UE_5.3\...
        super(UnrealVersion, self).__init__(version, patch='0')


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


Application = UnrealApplication()
