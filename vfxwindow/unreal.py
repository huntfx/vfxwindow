"""Window class for Unreal."""

from __future__ import absolute_import

import os
import sys

import unreal

from .utils import setCoordinatesToScreen
from .standalone import StandaloneWindow


UNREAL_VERSION = sys.executable.split(os.path.sep)[-5][3:]


class UnrealWindow(StandaloneWindow):
    def __init__(self, parent=None, **kwargs):
        super(UnrealWindow, self).__init__(parent, **kwargs)
        self.unreal = True
        self.standalone = False

        # Parenting external windows was only added in 4.20
        try:
            unreal.parent_external_window_to_slate(self.winId())
        except AttributeError:
            pass

    def saveWindowPosition(self):
        """Save the window location."""
        try:
            unrealSettings = self.windowSettings['unreal']
        except KeyError:
            unrealSettings = self.windowSettings['unreal'] = {}
        try:
            mainWindowSettings = unrealSettings['main']
        except KeyError:
            mainWindowSettings = unrealSettings['main'] = {}
        mainWindowSettings['width'] = self.width()
        mainWindowSettings['height'] = self.height()
        mainWindowSettings['x'] = self.x()
        mainWindowSettings['y'] = self.y()

        super(UnrealWindow, self).saveWindowPosition()

    def loadWindowPosition(self):
        """Set the position of the window when loaded."""
        try:
            width = self.windowSettings['unreal']['main']['width']
            height = self.windowSettings['unreal']['main']['height']
            x = self.windowSettings['unreal']['main']['x']
            y = self.windowSettings['unreal']['main']['y']
        except KeyError:
            super(UnrealWindow, self).loadWindowPosition()
        else:
            x, y = setCoordinatesToScreen(x, y, width, height, padding=5)
            self.resize(width, height)
            self.move(x, y)

    @classmethod
    def show(cls, **kwargs):
        try:
            cls.clearWindowInstance(cls.WindowID)
        except AttributeError:
            pass
        return super(UnrealWindow, cls).show(instance=True, exec_=False)
