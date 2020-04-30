"""Window class for standalone use."""

from __future__ import absolute_import

import sys
from functools import partial
from multiprocessing import Queue, Process
from Qt import QtWidgets, IsPySide, IsPyQt4, IsPySide2, IsPyQt5

from .abstract import AbstractWindow
from .utils import setCoordinatesToScreen, hybridmethod


class _MultiAppLaunch(Process):
    """Launch multiple QApplications as separate processes."""

    def __init__(self, cls, *args, **kwargs):
        self.cls = cls
        self.args = args
        self.kwargs = kwargs
        super(_MultiAppLaunch, self).__init__()

    def run(self):
        """Launch the app once the process has started."""
        try:
            app = QtWidgets.QApplication(sys.argv)
        except RuntimeError:
            app = QtWidgets.QApplication.instance()
        window = super(StandaloneWindow, self.cls).show(*self.args, **self.kwargs)
        if isinstance(app, QtWidgets.QApplication):
            app.setActiveWindow(window)
        sys.exit(app.exec_())


class StandaloneWindow(AbstractWindow):
    """Window to use outside of specific programs."""

    def __init__(self, parent=None):
        super(StandaloneWindow, self).__init__(parent)
        self.standalone = True

    @hybridmethod
    def show(cls, self, *args, **kwargs):
        """Start a standalone QApplication and launch the window.
        Multiprocessing can be used to launch a separate application instead of an instance.
        The disadvantage of an instance is the palette and other bits are all linked.
        """
        # Window is already initialised
        if self is not cls:
            return super(StandaloneWindow, self).show()

        # Open a new window
        instance = kwargs.pop('instance', False)
        exec_ = kwargs.pop('exec_', True)

        window = None
        try:
            app = QtWidgets.QApplication(sys.argv)
            window = super(StandaloneWindow, cls).show(*args, **kwargs)
            if isinstance(app, QtWidgets.QApplication):
                app.setActiveWindow(window)
        except RuntimeError:
            if instance:
                app = QtWidgets.QApplication.instance()
                window = super(StandaloneWindow, cls).show(*args, **kwargs)
                if isinstance(app, QtWidgets.QApplication):
                    app.setActiveWindow(window)
                if exec_:
                    app.exec_()
            else:
                _MultiAppLaunch(cls, *args, **kwargs).start()
        else:
            if exec_:
                sys.exit(app.exec_())
        return window

    def windowPalette(self):
        currentPalette = super(StandaloneWindow, self).windowPalette()
        if currentPalette is None:
            if IsPySide or IsPyQt4:
                return 'Qt.4'
            elif IsPySide2 or IsPyQt5:
                return 'Qt.5'
        return currentPalette

    @classmethod
    def clearWindowInstance(cls, windowID):
        """Close the last class instance."""
        previousInstance = super(StandaloneWindow, cls).clearWindowInstance(windowID)
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
        self.clearWindowInstance(self.WindowID)
        return super(StandaloneWindow, self).closeEvent(event)

    def saveWindowPosition(self):
        """Save the window location."""
        if 'standalone' not in self.windowSettings:
            self.windowSettings['standalone'] = {}
        settings = self.windowSettings['standalone']

        key = self._getSettingsKey()
        if key not in settings:
            settings[key] = {}

        settings[key]['width'] = self.width()
        settings[key]['height'] = self.height()
        settings[key]['x'] = self.x()
        settings[key]['y'] = self.y()

        return super(StandaloneWindow, self).saveWindowPosition()

    def loadWindowPosition(self):
        """Set the position of the window when loaded."""
        key = self._getSettingsKey()
        try:
            x = self.windowSettings['standalone'][key]['x']
            y = self.windowSettings['standalone'][key]['y']
            width = self.windowSettings['standalone'][key]['width']
            height = self.windowSettings['standalone'][key]['height']
        except KeyError:
            super(StandaloneWindow, self).loadWindowPosition()
        else:
            x, y = setCoordinatesToScreen(x, y, width, height, padding=5)
            self.resize(width, height)
            self.move(x, y)
