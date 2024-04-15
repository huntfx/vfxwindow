
"""Window class for 3ds Max."""

from __future__ import absolute_import, print_function

from Qt import QtWidgets

import MaxPlus

from .application import Application
from ..abstract.gui import AbstractWindow
from ..utils import hybridmethod, setCoordinatesToScreen


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
    """Window to use for 3ds Max."""

    def __init__(self, parent=None, **kwargs):
        if parent is None:
            parent = getMainWindow()
        super(MaxWindow, self).__init__(parent, **kwargs)

    @property
    def application(self):
        """Get the current application."""
        return Application

    def saveWindowPosition(self):
        """Save the window location."""
        if self.application in self.windowSettings:
            settings = self.windowSettings[self.application]
        else:
            settings = self.windowSettings[self.application] = {}

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
        try:
            settings = self.windowSettings[self.application][self._getSettingsKey()]
            width = settings['width']
            height = settings['height']
            x = settings['x']
            y = settings['y']
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
            return 'Max.{}'.format(int(self.application.version))
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

    @classmethod
    def dialog(cls, parent=None, *args, **kwargs):
        """Create the window as a dialog."""
        if parent is None:
            parent = getMainWindow()
        return super(MaxWindow, cls).dialog(parent=parent, *args, **kwargs)

    def closeEvent(self, event):
        """Save the position before closing."""
        self.saveWindowPosition()
        return super(MaxWindow, self).closeEvent(event)
