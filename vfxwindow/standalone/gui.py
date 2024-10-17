"""Window class for standalone use."""

from __future__ import absolute_import

import sys
from Qt import QtWidgets, IsPySide, IsPyQt4, IsPySide2, IsPyQt5

from ..application import Blender, RenderDoc
from ..abstract.gui import AbstractWindow
from ..utils import setCoordinatesToScreen, hybridmethod

# Skip the multiprocessing import for certain apps
# Blender 4.2 becomes unstable and starts crashing
# RenderDoc fails with `ModuleNotFoundError: No module named '_socket'`
if (Blender and Blender.version > 4) or RenderDoc:
    Process = object
else:
    from multiprocessing import Process


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

    @property
    def application(self):
        """Get the current application."""
        return None

    @hybridmethod
    def show(cls, self, *args, **kwargs):
        """Start a standalone QApplication and launch the window.

        Launch Parameters:
            init (bool): If the QApplication should be initialised.
                Set to False if this causes a program crash on startup.
            instance (bool): If a QApplication instance should be used.
                If False, then a new process will be started instead.
                Note that all instanced apps will share the same
                features such as palettes.
            exec_ (bool): If the QApplication should be executed.
                This is typically blocking but each application reacts
                differently. It is best left off by default, and only
                enabled if the window won't stay open.

        Multiprocessing can be used to launch a separate application instead of an instance.
        The disadvantage of an instance is the palette and other bits are all linked.
        """
        # Window is already initialised
        if self is not cls:
            return super(StandaloneWindow, self).show()

        # Open a new window
        init = kwargs.pop('init', True)
        instance = kwargs.pop('instance', False)
        exec_ = kwargs.pop('exec_', True)

        window = None
        try:
            if not init:
                raise RuntimeError
            app = QtWidgets.QApplication(sys.argv)
            window = super(StandaloneWindow, cls).show(*args, **kwargs)
            if isinstance(app, QtWidgets.QApplication):
                app.setActiveWindow(window)
        except RuntimeError:
            if instance or Process is object:
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

    def setWindowPalette(self, program, version=None, style=True, force=False):
        """Set the palette of the window.
        If this window is parented to another VFXWindow, then skip as
        to not override its colour scheme.
        """
        if not force:
            for widget in QtWidgets.QApplication.topLevelWidgets():
                if widget != self and isinstance(widget, AbstractWindow) and not widget.isInstance():
                    return
        super(StandaloneWindow, self).setWindowPalette(program, version, style)

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
        if None in self.windowSettings:
            settings = self.windowSettings['standalone']
        else:
            settings = self.windowSettings['standalone'] = {}

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
            settings = self.windowSettings['standalone'][self._getSettingsKey()]
            x = settings['x']
            y = settings['y']
            width = settings['width']
            height = settings['height']
        except KeyError:
            super(StandaloneWindow, self).loadWindowPosition()
        else:
            x, y = setCoordinatesToScreen(x, y, width, height, padding=5)
            self.resize(width, height)
            self.move(x, y)
