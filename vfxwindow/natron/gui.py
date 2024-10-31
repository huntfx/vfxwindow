"""Window class for Natron.

TODO:
    NatronGui.natron.getGuiInstance(0).registerPythonPanel - https://natron.readthedocs.io/en/v2.3.15/devel/PythonReference/NatronGui/PyPanel.html
"""

from __future__ import absolute_import

import NatronEngine
import NatronGui

from .application import Application
from ..utils import setCoordinatesToScreen, hybridmethod
from ..standalone.gui import StandaloneWindow


def getActiveGuiApp():
    """Get the active GUI app."""
    numInstances = NatronGui.natron.getNumInstances()
    if numInstances == 1:
        return NatronGui.natron.getGuiInstance(0)
    active = NatronGui.natron.getActiveInstance()
    for i in range(numInstances):
        instance = NatronGui.natron.getInstance(i)
        if id(instance) == id(active):
            return NatronGui.natron.getGuiInstance(i)
    return None


class NatronWindow(StandaloneWindow):
    """Window to use for Natron."""

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

        super(NatronWindow, self).saveWindowPosition()

    def loadWindowPosition(self):
        """Set the position of the window when loaded."""
        try:
            settings = self.windowSettings[self.application][self._getSettingsKey()]
            width = settings['width']
            height = settings['height']
            x = settings['x']
            y = settings['y']
        except KeyError:
            super(NatronWindow, self).loadWindowPosition()
        else:
            x, y = setCoordinatesToScreen(x, y, width, height, padding=5)
            self.resize(width, height)
            self.move(x, y)

    @hybridmethod
    def show(cls, self, *args, **kwargs):
        # Window is already initialised
        if self is not cls:
            return super(NatronWindow, self).show()

        # Close down window if it exists and open a new one
        try:
            cls.clearWindowInstance(cls.WindowID)
        except AttributeError:
            pass
        kwargs['init'] = False
        kwargs['exec_'] = False
        kwargs['instance'] = True
        return super(NatronWindow, cls).show(*args, **kwargs)
