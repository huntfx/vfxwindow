"""Window class for standalone use."""

from __future__ import absolute_import

import sys
from Qt import QtWidgets, IsPySide, IsPyQt4, IsPySide2, IsPyQt5

from ..application import Blender, RenderDoc
from ..abstract.gui import AbstractWindow
from ..utils import setCoordinatesToScreen, hybridmethod

# Skip the multiprocessing import for certain apps
# RenderDoc fails with `ModuleNotFoundError: No module named '_socket'`
if RenderDoc:
    Process = object
# Somewhere between Blender 3.6 and 4.2 it became unstable and would crash
# The exact version isn't known, but it was fixed in 4.2.4 and 4.3.0
# https://projects.blender.org/blender/blender/commit/9a252c2e73b9303d4c2c493c7a80a75a4b1629bc
elif Blender and Blender.version == 4 and Blender.version < '4.2.4':
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
        inst = super(StandaloneWindow, cls).clearWindowInstance(windowID)
        if inst is None:
            return None

        #Shut down the window
        if not inst['window'].isClosed():
            try:
                inst['window'].close()
            except (RuntimeError, ReferenceError):
                pass

        return inst

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
