"""Window class for Unreal."""

from __future__ import absolute_import

import os
import sys

import unreal

from .utils import setCoordinatesToScreen, hybridmethod
from .standalone import StandaloneWindow


VERSION = sys.executable.split(os.path.sep)[-5][3:]


class UnrealWindow(StandaloneWindow):
    """Window to use for Unreal."""

    def __init__(self, parent=None, **kwargs):
        super(UnrealWindow, self).__init__(parent, **kwargs)

        self.unreal = True  #: .. deprecated:: 1.9.0 Use :property:`~AbstractWindow.application` instead.
        self.standalone = False  #: .. deprecated:: 1.9.0

        # Parenting external windows was only added in 4.20
        try:
            unreal.parent_external_window_to_slate(self.winId())
        except AttributeError:
            pass

    @property
    def application(self):
        return 'Unreal Engine'

    def saveWindowPosition(self):
        """Save the window location."""
        if self.application not in self.windowSettings:
            self.windowSettings[self.application] = {}
        settings = self.windowSettings[self.application]

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
        key = self._getSettingsKey()
        try:
            width = self.windowSettings[self.application][key]['width']
            height = self.windowSettings[self.application][key]['height']
            x = self.windowSettings[self.application][key]['x']
            y = self.windowSettings[self.application][key]['y']
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
