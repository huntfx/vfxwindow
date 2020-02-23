"""Window class for Blackmagic Fusion."""

from __future__ import absolute_import

import os
import sys

try:
    import fusionscript
    fusion = fusionscript.scriptapp('Fusion')
except ImportError:
    import PeyeonScript as eyeon
    fusion = eyeon.scriptapp('Fusion')

from .utils import setCoordinatesToScreen, hybridmethod
from .standalone import StandaloneWindow


VERSION = str(int(fusion.Version))


def getMainWindow():
    """Get a pointer to the Fusion window.
    However as of Fusion 9, this doesn't seem to return anything.
    """

    return fusion.GetMainWindow()


class FusionWindow(StandaloneWindow):
    def __init__(self, parent=None, **kwargs):
        if parent is None:
            parent = getMainWindow()
        super(FusionWindow, self).__init__(parent, **kwargs)
        self.fusion = True
        self.standalone = False

    def saveWindowPosition(self):
        """Save the window location."""

        if 'fusion' not in self.windowSettings:
            self.windowSettings['fusion'] = {}
        settings = self.windowSettings['fusion']

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

        key = self._getSettingsKey()
        try:
            width = self.windowSettings['fusion'][key]['width']
            height = self.windowSettings['fusion'][key]['height']
            x = self.windowSettings['fusion'][key]['x']
            y = self.windowSettings['fusion'][key]['y']
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
