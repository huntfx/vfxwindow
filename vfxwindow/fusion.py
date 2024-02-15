"""Window class for Blackmagic Fusion."""

from __future__ import absolute_import

import os
import sys

try:
    import fusionscript
    fusion = fusionscript.scriptapp('Fusion')
except ImportError:
    import PeyeonScript
    fusion = PeyeonScript.scriptapp('Fusion')

from .application import Fusion as App
from .utils import setCoordinatesToScreen, hybridmethod
from .standalone import StandaloneWindow


def getMainWindow():
    """Get a pointer to the Fusion window.
    However as of Fusion 9, this doesn't seem to return anything.
    """
    if fusion is None:
        return None
    return fusion.GetMainWindow()


class FusionWindow(StandaloneWindow):
    """Window to use for Blackmagic Fusion."""

    Application = App

    def __init__(self, parent=None, **kwargs):
        if parent is None:
            parent = getMainWindow()
        super(FusionWindow, self).__init__(parent, **kwargs)

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

        super(FusionWindow, self).saveWindowPosition()

    def loadWindowPosition(self):
        """Set the position of the window when loaded."""
        try:
            settings = self.windowSettings[self.application][self._getSettingsKey()]
            width = settings['width']
            height = settings['height']
            x = settings['x']
            y = settings['y']
        except KeyError:
            super(FusionWindow, self).loadWindowPosition()
        else:
            x, y = setCoordinatesToScreen(x, y, width, height, padding=5)
            self.resize(width, height)
            self.move(x, y)

    @hybridmethod
    def show(cls, self, *args, **kwargs):
        """Show the Fusion window."""
        # Window is already initialised
        if self is not cls:
            return super(FusionWindow, self).show()

        # Close down window if it exists and open a new one
        try:
            cls.clearWindowInstance(cls.WindowID)
        except AttributeError:
            pass
        kwargs['exec_'] = True
        return super(FusionWindow, cls).show(*args, **kwargs)

    @classmethod
    def dialog(cls, parent=None, *args, **kwargs):
        """Create the window as a dialog."""
        if parent is None:
            parent = getMainWindow()
        return super(FusionWindow, cls).dialog(parent=parent, *args, **kwargs)
