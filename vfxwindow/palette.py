"""Code for saving and loading palettes from different programs.

Source (heavily modified): https://github.com/fredrikaverpil/pyvfx-boilerplate/blob/master/boilerlib/mayapalette.py
"""

from __future__ import absolute_import

import json
import os
from string import ascii_letters, digits

from .utils.Qt import QtGui, QtWidgets


PALETTE_ROLE = QtGui.QPalette.ColorRole

PALETTE_GROUP = QtGui.QPalette.ColorGroup

DIR = os.path.join(os.path.dirname(__file__), 'palettes')

FILE_EXT = 'json'


def getPaletteObjects():
    """Get the available group/role objects."""
    roles = []
    groups = []
    for attrName in dir(QtGui.QPalette):
        attrObj = getattr(QtGui.QPalette, attrName)
        if isinstance(attrObj, PALETTE_ROLE) and attrObj != PALETTE_ROLE.NColorRoles:
            roles.append(attrObj)
        if isinstance(attrObj, PALETTE_GROUP) and attrObj not in (PALETTE_GROUP.NColorGroups, PALETTE_GROUP.All):
            groups.append(attrObj)
    return {PALETTE_ROLE: roles, PALETTE_GROUP: groups}


def getPaletteColours(palette=None):
    """Return the colours of the current palette."""
    if palette is None:
        palette = QtGui.QPalette()

    paletteObjects = getPaletteObjects()
    paletteData = {}
    for role in paletteObjects[PALETTE_ROLE]:
        for group in paletteObjects[PALETTE_GROUP]:
            paletteData['{}:{}'.format(role.name.decode('ascii'), group.name.decode('ascii'))] = palette.color(group, role).rgb()
    return paletteData


def savePaletteData(program, version=None, palette=None):
    """Save the current palette colours in a json file."""
    paletteData = json.dumps(getPaletteColours(palette), indent=2)

    program = ''.join(i for i in str(program) if i in ascii_letters)
    if version is not None:
        version = ''.join(i for i in str(version) if i in digits or i == '.')
        fileName = '{}.{}.{}'.format(program, version, FILE_EXT)
    else:
        fileName = '{}.{}'.format(program, FILE_EXT)
    filePath = os.path.join(DIR, fileName)

    with open(filePath, 'w') as f:
        f.write(paletteData)
    return filePath


def readPalette(filePath):
    """Read the contents of a palette file."""
    with open(filePath, 'r') as f:
        return json.loads(f.read())


def setStyle(style=None):
    """Set the style of the window.
    WARNING: Only do this on standalone windows or it'll mess up the program.
    """
    availableStyles = getStyleList()
    if style not in availableStyles:
        if 'Fusion' in availableStyles:
            style = 'Fusion'
        elif 'Plastique' in availableStyles:
            style = 'Plastique'
        else:
            return
    QtWidgets.QApplication.setStyle(style)


def setPalette(program, version=None, style=True):
    """Apply a palette to the current window."""
    if version is None:
        paletteName = '{}.{}'.format(program, FILE_EXT)
    else:
        paletteName = '{}.{}.{}'.format(program, version, FILE_EXT)
    paletteFile = os.path.join(DIR, paletteName)
    paletteData = readPalette(paletteFile)

    palette = QtGui.QPalette()
    for paletteType, colour in paletteData.items():
        roleName, groupName = paletteType.split(':')
        try:
            role = getattr(PALETTE_ROLE, roleName)
            group = getattr(PALETTE_GROUP, groupName)
        except AttributeError:
            continue
        if role is not None and group is not None:
            palette.setColor(group, role, QtGui.QColor(colour))

    QtWidgets.QApplication.setPalette(palette)
    if style:
        setStyle()


def getPaletteList():
    """Return a sorted list of available palettes starting with the default ones."""
    ext = '.' + FILE_EXT
    extLen = len(ext)
    palettes = set(i[:-extLen] for i in os.listdir(DIR) if i[-extLen:] == ext)
    defaultPalettes = set(i for i in palettes if i.startswith('Qt.'))
    return sorted(defaultPalettes) + sorted(palettes - defaultPalettes)


def getStyleList():
    """Return a list of all available styles."""
    return QtWidgets.QStyleFactory.keys()


def matchPaletteToFile():
    """Find which file the current palette relates to."""
    currentPalette = getPaletteColours()
    files = getPaletteList()
    files = ['Nuke.10']
    for fileName in files:
        filePath = os.path.join(DIR, '{}.{}'.format(fileName, FILE_EXT))
        paletteData = readPalette(filePath)
        if paletteData == currentPalette:
            return fileName
    return None


if __name__ == '__main__':
    savePaletteData('loaded-program', 'program-version')
