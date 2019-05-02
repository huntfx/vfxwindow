"""Window class for standalone use."""

from __future__ import absolute_import

import sys
from functools import partial
from multiprocessing import Queue, Process
from threading import Thread

from .base import BaseWindow
from .utils import setCoordinatesToScreen
from .utils.Qt import QtWidgets, IsPySide, IsPyQt4, IsPySide2, IsPyQt5


class _MultiAppLaunch(Process):
    """Launch multiple QApplications."""
    def __init__(self, cls):
        self.cls = cls
        super(_MultiAppLaunch, self).__init__()
    
    def run(self):
        app = QtWidgets.QApplication(sys.argv)
        window = super(StandaloneWindow, self.cls).show()
        app.setActiveWindow(window)
        sys.exit(app.exec_())


class StandaloneWindow(BaseWindow):
    """Window to use outside of specific programs."""
    def __init__(self, parent=None):
        super(StandaloneWindow, self).__init__(parent)
        self.standalone = True

    @classmethod
    def show(cls, instance=False, **kwargs):
        """Start a standalone QApplication and launch the window.
        Multiprocessing can be used to launch a separate application instead of an instance.
        The disadvantage of an instance is the palette and other bits are all linked.
        """
        if instance:
            try:
                app = QtWidgets.QApplication(sys.argv)
                window = super(StandaloneWindow, cls).show()
                app.setActiveWindow(window)
            except RuntimeError:
                app = QtWidgets.QApplication.instance()
                window = super(StandaloneWindow, cls).show()
                app.setActiveWindow(window)
            else:
                sys.exit(app.exec_())
        else:
            _MultiAppLaunch(cls).start()

    def setWindowPalette(self, program, version=None):
        """Override of the default setWindowPalette to also set style."""
        return super(StandaloneWindow, self).setWindowPalette(program, version, style=True)

    def windowPalette(self):
        currentPalette = super(StandaloneWindow, self).windowPalette()
        if currentPalette is None:
            if IsPySide or IsPyQt4:
                return 'Qt.4'
            elif IsPySide2 or IsPyQt5:
                return 'Qt.5'
        return currentPalette

    @classmethod
    def clearWindowInstance(self, windowID):
        """Close the last class instance."""
        previousInstance = super(StandaloneWindow, self).clearWindowInstance(windowID)
        if previousInstance is None:
            return

        #Shut down the window
        if not previousInstance['window'].isClosed():
            try:
                previousInstance['window'].close()
            except (RuntimeError, ReferenceError):
                pass

    def closeEvent(self, event):
        """Save the window location on window close."""
        self.saveWindowPosition()
        self.clearWindowInstance(self.ID)
        return super(StandaloneWindow, self).closeEvent(event)

    def saveWindowPosition(self):
        """Save the window location."""
        if 'standalone' not in self.windowSettings:
            self.windowSettings['standalone'] = {}
        if 'main' not in self.windowSettings['standalone']:
            self.windowSettings['standalone']['main'] = {}

        self.windowSettings['standalone']['main']['width'] = self.width()
        self.windowSettings['standalone']['main']['height'] = self.height()
        self.windowSettings['standalone']['main']['x'] = self.x()
        self.windowSettings['standalone']['main']['y'] = self.y()
        return super(StandaloneWindow, self).saveWindowPosition()

    def loadWindowPosition(self):
        """Set the position of the window when loaded."""
        try:
            x = self.windowSettings['standalone']['main']['x']
            y = self.windowSettings['standalone']['main']['y']
            width = self.windowSettings['standalone']['main']['width']
            height = self.windowSettings['standalone']['main']['height']
        except KeyError:
            super(StandaloneWindow, self).loadWindowPosition()
        else:
            x, y = setCoordinatesToScreen(x, y, width, height, padding=5)
            self.resize(width, height)
            self.move(x, y)
