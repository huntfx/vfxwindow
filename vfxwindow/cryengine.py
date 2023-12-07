"""Window class for CryEngine."""

from __future__ import absolute_import

import os
import sys

from Qt import QtWidgets

import SandboxBridge

from .abstract import getWindowSettings
from .utils import setCoordinatesToScreen, hybridmethod
from .standalone import StandaloneWindow


try:
    VERSION = float(sys.executable.split(os.path.sep)[-4].rsplit('.', 1)[0])
except (TypeError, IndexError):
    VERSION = None


def getMainWindow():
    """Get a pointer to the CryEngine window.
    This doesn't appear to make any difference to a standalone window.
    """

    for widget in QtWidgets.QApplication.topLevelWidgets():
        if type(widget) == QtWidgets.QWidget and widget.parentWidget() is None and widget.objectName() == 'mainWindow':
            return widget


class CryWindow(StandaloneWindow):
    def __init__(self, parent=None, **kwargs):
        if parent is None:
            parent = getMainWindow()
        super(CryWindow, self).__init__(parent, **kwargs)
        
        self.cryengine = True  #: .. deprecated:: 1.9.0 Use :property:`~AbstractWindow.software` instead.
        self.standalone = False  #: .. deprecated:: 1.9.0 Won't be needed anymore when using :property:`~AbstractWindow.software`.

    @property
    def software(self):
        return 'CryEngine'

    def saveWindowPosition(self):
        """Save the window location."""

        if self.software not in self.windowSettings:
            settings = self.windowSettings[self.software] = {}

        settings['docked'] = self.dockable(raw=True)

        if self.dockable():
            pass  # Not yet implemented

        else:
            settings['main'] = dict(
                width=self.width(),
                height=self.height(),
                x=self.x(),
                y=self.y(),
            )

        super(CryWindow, self).saveWindowPosition()

    def loadWindowPosition(self):
        """Set the position of the window when loaded."""

        if self.dockable():
            return  # Not yet implemented

        try:
            settings = self.windowSettings[self.software]['main']
            width = settings['width']
            height = settings['height']
            x = settings['x']
            y = settings['y']
        except KeyError:
            super(CryWindow, self).loadWindowPosition()
        else:
            x, y = setCoordinatesToScreen(x, y, width, height, padding=5)
            self.resize(width, height)
            self.move(x, y)

    @hybridmethod
    def show(cls, self, *args, **kwargs):
        # Window is already initialised
        if self is not cls:
            return super(CryWindow, self).show()

        # Close down any instances of the window
        try:
            cls.clearWindowInstance(cls.WindowID)
        except AttributeError:
            settings = {}
        else:
            settings = getWindowSettings(cls.WindowID)

        #Load settings
        if hasattr(cls, 'WindowDockable'):
            docked = cls.WindowDockable
        else:
            try:
                docked = settings[self.software]['docked']
            except KeyError:
                try:
                    docked = cls.WindowDefaults['docked']
                except (AttributeError, KeyError):
                    docked = True

        # Apparently this should add the window to the "Tools" menu,
        # but I couldn't figure it out so it's disabled for now
        if False and docked:
            return SandboxBridge.register_window(
                window_type=cls,
                name=getattr(cls, 'WindowName', 'New Window'),
            )

        kwargs['exec_'] = False
        kwargs['instance'] = True
        return super(CryWindow, cls).show(*args, **kwargs)
