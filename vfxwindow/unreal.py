"""Window class for Unreal."""

from __future__ import absolute_import

import os
import sys

import unreal

from .application import Unreal as App
from .utils import setCoordinatesToScreen, hybridmethod
from .standalone import StandaloneWindow


class UnrealWindow(StandaloneWindow):
    """Window to use for Unreal."""

    Application = App

    def __init__(self, parent=None, **kwargs):
        super(UnrealWindow, self).__init__(parent, **kwargs)

        # Parenting external windows was only added in 4.20
        try:
            unreal.parent_external_window_to_slate(self.winId())
        except AttributeError:
            pass

    def saveWindowPosition(self):
        """Save the window location."""
        if self.application.camelCase() in self.windowSettings:
            settings = self.windowSettings[self.application.camelCase()]
        else:
            settings = self.windowSettings[self.application.camelCase()] = {}

        key = self._getSettingsKey()
        if key not in settings:
            settings[key] = {}

        settings[key]['width'] = self.width()
        settings[key]['height'] = self.height()
        settings[key]['x'] = self.x()
        settings[key]['y'] = self.y()

        super(UnrealWindow, self).saveWindowPosition()

    def loadWindowPosition(self):
        """Set the position of the window when loaded."""
        try:
            settings = self.windowSettings[self.application.camelCase()][self._getSettingsKey()]
            width = settings['width']
            height = settings['height']
            x = settings['x']
            y = settings['y']
        except KeyError:
            super(UnrealWindow, self).loadWindowPosition()
        else:
            x, y = setCoordinatesToScreen(x, y, width, height, padding=5)
            self.resize(width, height)
            self.move(x, y)

    @hybridmethod
    def show(cls, self, *args, **kwargs):
        # Window is already initialised
        if self is not cls:
            return super(UnrealWindow, self).show()

        # Close down window if it exists and open a new one
        try:
            cls.clearWindowInstance(cls.WindowID)
        except AttributeError:
            pass
        kwargs['instance'] = True
        kwargs['exec_'] = False
        return super(UnrealWindow, cls).show(*args, **kwargs)
