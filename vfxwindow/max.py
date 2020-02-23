
"""Window class for 3D Studio Max."""

from __future__ import absolute_import, print_function

import os
import sys

import MaxPlus

from .abstract import AbstractWindow, getWindowSettings
from .utils import hybridmethod, setCoordinatesToScreen
from .utils.Qt import QtWidgets, QtCompat, QtCore
from .standalone import StandaloneWindow


VERSION = sys.executable.split(os.path.sep)[-2][8:]


def getMainWindow():
    """Returns the main window.

    Source: https://stackoverflow.com/a/46739609/2403000, https://autode.sk/36jLSbE
    """
    try:
        return MaxPlus.GetQMaxMainWindow()
    except AttributeError:
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if type(widget) == QtWidgets.QWidget and widget.parentWidget() is None:
                return widget


class MaxWindow(AbstractWindow):
    def __init__(self, parent=None, **kwargs):
        if parent is None:
            parent = getMainWindow()
        super(MaxWindow, self).__init__(parent, **kwargs)
        self.max = True

    def saveWindowPosition(self):
        """Save the window location."""

        if 'max' not in self.windowSettings:
            self.windowSettings['max'] = {}
        settings = self.windowSettings['max']

        key = self._getSettingsKey()
        if key not in settings:
            settings[key] = {}

        settings[key]['width'] = self.width()
        settings[key]['height'] = self.height()
        settings[key]['x'] = self.x()
        settings[key]['y'] = self.y()

        super(MaxWindow, self).saveWindowPosition()

    def loadWindowPosition(self):
        """Set the position of the window when loaded."""

        key = self._getSettingsKey()
        try:
            width = self.windowSettings['max'][key]['width']
            height = self.windowSettings['max'][key]['height']
            x = self.windowSettings['max'][key]['x']
            y = self.windowSettings['max'][key]['y']
        except KeyError:
            super(MaxWindow, self).loadWindowPosition()
        else:
            x, y = setCoordinatesToScreen(x, y, width, height, padding=5)
            self.resize(width, height)
            self.move(x, y)

    def setWindowPalette(self, program, version=None, style=True, force=False):
        """Set the palette of the window.
        This affects the entire 3DS Max GUI so it's disabled by default.
        The force parameter can be set to override this behaviour.
        """

        if force or self.batch:
            super(MaxWindow, self).setWindowPalette(program, version, style)

    def windowPalette(self):
        """Get the current window palette."""

        currentPalette = super(MaxWindow, self).windowPalette()
        if currentPalette is None:
            return 'Max.{}'.format(VERSION)
        return currentPalette

    @hybridmethod
    def show(cls, self, *args, **kwargs):
        """Show the 3DS Max window."""

        # Window is already initialised
        if self is not cls:
            return super(MaxWindow, self).show()

        # Close down window if it exists and open a new one
        try:
            cls.clearWindowInstance(cls.WindowID)
        except AttributeError:
            pass
        return super(MaxWindow, cls).show(*args, **kwargs)

    def closeEvent(self, event):
        """Save the position before closing."""

        self.saveWindowPosition()
        return super(MaxWindow, self).closeEvent(event)
