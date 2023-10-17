import sys
import os
import re

from .. import exceptions


def __importable(programImport):
    """Test if the given module import string can be imported.

    If the import string of a DCC can be imported, it's likely that we're in the software
    environment. This is not 100% accurate so it should be paired with another test to 
    lower the risk of false positive.

    ..notes:: 
        Instead of testing if the string can be imported using `pkgutil.find_loader` or 
        `importlib.util.find_spec` that import the module and then seems to remove it from
        sys.modules, we go with the basic `__import__` function. 
        Keeping the modules already imported shouldn't do anything than speed up future 
        imports. Also, if the other hand, if it's already in sys.modules it can be imported.
    """
    if programImport in sys.modules:
        return True

    try:
        return bool(__import__(programImport))
    except (ModuleNotFoundError, ImportError):
        return False


_MAYA = \
(
    r'^[A-Z]:\\Program\sFiles(?:|\s\(x86\))\\[aA]utodesk\\[mM]aya\d{4}\\bin\\[mM]aya\.exe$',  # Windows
    r'^/usr/[aA]utodesk/[mM]aya(?:\d{4})?/bin/[mM]aya\.bin$',  # Linux
    r'^/Applications/[mM]aya\s\d{4}/[mM]aya\.app$',  # MacOs
    r'^.*(?:\\|/)bin(?:\\|/)[mM]aya\.(?:bin|exe|app)$',  # Common
    r'^.*(?:\\|/)[mM]aya\.(?:bin|exe|app)$',  # Common
)

_MAYA_BATCH = \
(
    r'^[A-Z]:\\Program\sFiles(?:|\s\(x86\))\\[aA]utodesk\\[mM]aya\d{4}\\(?:bin|bin2|bin\\\.\.\\bin2)\\[mM]ayapy[2]?\.exe$',  # Windows
    r'^/usr/[aA]utodesk/[mM]aya\d{4}/(?:bin|bin2|bin/\.\./bin2)/[pP]ython-bin$',  # Linux
    r'[mM]ayapy\.(?:bin|exe|app)',  # Common
)

_HOUDINI = \
(
    r'[hH]oudini\.(?:bin|exe|app)',  # Windows, MacOS
    r'hfs\d+\.\d+\.\d+',  # Linux
    r'hindie-bin',  # Indie
)

_UNREAL_ENGINE = \
(
    r'[uU]nreal[eE](?:ngine|ditor)\.(?:bin|exe)',
    r'.*?_[uU]nreal_[eE]ngine_\d+\.\d+\.\d+',
    r'[uU]nreal[eE](?:ngine|ditor)',
    r'(?:ue|UE)\d+[eE]ditor',
)

_BLENDER = \
(
    r'[bB]lender[_\s][fF]oundation',
    r'[bB]lender[_\s]\d+(?:\.\d+){0,2}',
    r'[bB]lender\.(?:bin|exe)',
)

_NUKE = \
(
    r'[nN]uke\d+(?:\.\d+){0,2}\.(?:bin|exe|app)',
    r'[nN]uke\.(?:bin|exe|app)',
)

_KATANA = \
(
    r'[kK]atana\d+(?:\.\d+){0,2}\.(?:bin|exe|app)',
    r'[kK]atana\.(?:bin|exe|app)',
)

_MARI = \
(
    r'[mM]ari\d+(?:\.\d+){0,2}\.(?:bin|exe|app)',
    r'[mM]ari\.(?:bin|exe|app)',
)

_MODO = \
(
    r'[mM]odo\d+(?:\.\d+){0,2}\.(?:bin|exe|app)',
    r'[mM]odo\.(?:bin|exe|app)',
)

_HIERO = \
(
    r'[hH]iero\d+(?:\.\d+){0,2}\.(?:bin|exe|app)',
    r'[hH]iero\.(?:bin|exe|app)',
)

_3DS_MAX = \
(
    r'3ds[mM]ax\.(?:bin|exe|app)',
)

_MOTION_BUILDER = \
(
    r'^.*(?:\\|/)[mM]otion[bB]uilder\d{4}(?:\\|/)[mM]otion[bB]uilder\.(?:bin|exe|app)'
    r'[mM]otion[bB]uilder\.(?:bin|exe|app)',
)

_SUBSTANCE_PAINTER = \
(
    r'[pP]ainter\.(?:bin|exe|app)',
    r'[sS]ubstance(?:_|\s)3[dD](?:_|\s)[pP]ainter',
)

_SUBSTANCE_DESIGNER = \
(
    r'[dD]esigner\.(?:bin|exe|app)',
    r'[sS]ubstance(?:_|\s)3[dD](?:_|\s)[dD]esigner',
)

_FUSION_360 = \
(
    r'[fF]usion\.(?:bin|exe|app)',
)


def isMaya():
    if any((re.search(pattern, sys.executable) for pattern in _MAYA)):
        return __importable('maya')
    return False


def isMayaBatch():
    if any((re.search(pattern, sys.executable) for pattern in _MAYA_BATCH)):
        return __importable('maya')
    return False


def isHoudini():
    if any((re.search(pattern, sys.executable) for pattern in _HOUDINI)):
        return __importable('hou')
    return False


def isUnrealEngine():
    if any((re.search(pattern, sys.executable) for pattern in _UNREAL_ENGINE)):
        return __importable('unreal')
    return False


def isBlender():
    if any((re.search(pattern, sys.executable) for pattern in _BLENDER)):
        return __importable('bpy')
    return False


def isNuke():
    if any((re.search(pattern, sys.executable) for pattern in _NUKE)):
        return __importable('bpy')
    return False


def isKatana():
    if any((re.search(pattern, sys.executable) for pattern in _KATANA)):
        raise vfxExceptions.NotImplementedApplicationError('No implementation found for Katana.')
        return __importable('katana')
    return False


def isMari():
    if any((re.search(pattern, sys.executable) for pattern in _MARI)):
        raise vfxExceptions.NotImplementedApplicationError('No implementation found for Mari.')
        return __importable('mari')
    return False


def isModo():
    if any((re.search(pattern, sys.executable) for pattern in _MODO)):
        raise vfxExceptions.NotImplementedApplicationError('No implementation found for Modo.')
        return __importable('lx')
    return False


def isHiero():
    if any((re.search(pattern, sys.executable) for pattern in _HIERO)):
        raise vfxExceptions.NotImplementedApplicationError('No implementation found for Hiero.')
        return __importable('hiero')
    return False


def is3dsMax():
    if any((re.search(pattern, sys.executable) for pattern in _3DS_MAX)):
        return __importable('pymxs') or __importable('MaxPlus')
    return False


def isMotionBuilder():
    if any((re.search(pattern, sys.executable) for pattern in _MOTION_BUILDER)):
        raise vfxExceptions.NotImplementedApplicationError('No implementation found for Motion Builder.')
        return __importable('pyfbsdk') and __importable('pyfbsdk_additions')
    return False


def isSubstancePainter():
    if any((re.search(pattern, sys.executable) for pattern in _SUBSTANCE_PAINTER)):
        return __importable('substance_painter')
    return False


def isSubstanceDesigner():
    if any((re.search(pattern, sys.executable) for pattern in _SUBSTANCE_DESIGNER)):
        return __importable('sd')
    return False


def isFusion360():
    if any((re.search(pattern, sys.executable) for pattern in _FUSION_360)):
        return __importable('fusionscript') or __importable('PeyeonScript')
    return False
