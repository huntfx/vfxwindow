"""Window class for Substance.

Help: https://docs.substance3d.com/sddoc/creating-user-interface-elements-172824940.html

TODO:
    APPLICATION.registerBeforeFileLoadedCallback(callable)
        Register a callback to be called before a file is loaded

    APPLICATION.registerAfterFileLoadedCallback(callable)
        Register a callback to be called after a file is loaded

    APPLICATION.registerBeforeFileSavedCallback(callable):
        Register a callback to be called before a file is saved

    APPLICATION.registerAfterFileSavedCallback(callable):
        Register a callback to be called after a file is saved

    APPLICATION.unregisterCallback(callbackID):
        Unregister a callback
"""

from __future__ import absolute_import

import os
import sys
import uuid
from Qt import QtWidgets

import sd

from .abstract import AbstractWindow, getWindowSettings
from .utils import setCoordinatesToScreen, hybridmethod


APPLICATION = sd.getContext().getSDApplication()

MANAGER = APPLICATION.getQtForPythonUIMgr()

VERSION = None  # TODO: Find out how to get the version


def getMainWindow():
    """Get the main application window."""

    return MANAGER.getMainWindow()


def dockWrap(windowClass, *args, **kwargs):
    """Create a docked window.
    This can only create it on the first run, afterwards the window
    must be relaunched from the menu.
    """

    # Set window ID if needed but disable saving
    if not hasattr(windowClass, 'WindowID'):
        windowClass.WindowID = str(uuid.uuid4())
        windowClass.saveWindowPosition = lambda *args, **kwargs: None
    windowInstance = windowClass(parent=None, dockable=True, *args, **kwargs)

    dock = MANAGER.newDockWidget(identifier=windowClass.WindowID, title=getattr(windowInstance, 'WindowName', 'New Window'))
    layout = QtWidgets.QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(windowInstance)
    dock.setLayout(layout)

    windowInstance.deferred(windowInstance.windowReady.emit)
    return windowInstance


def dialogWrap(windowClass, title=None, *args, **kwargs):
    """Create the window as a dialog."""

    if not hasattr(windowClass, 'WindowID'):
        windowClass.WindowID = str(uuid.uuid4())

    dialog = QtWidgets.QDialog(parent=getMainWindow())
    dialog.setWindowTitle(title)

    layout = QtWidgets.QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    windowClass.WindowDockable = False
    windowInstance = windowClass(*args, **kwargs)
    layout.addWidget(windowInstance)
    dialog.setLayout(layout)

    windowInstance.loadWindowPosition()
    windowInstance.windowReady.emit()
    dialog.exec_()
    windowInstance.saveWindowPosition()
    return windowInstance


class SubstanceWindow(AbstractWindow):
    def __init__(self, parent=None, dockable=False, **kwargs):
        if parent is None:
            parent = getMainWindow()
        super(SubstanceWindow, self).__init__(parent, **kwargs)
        self.substance = True
        self.setDockable(dockable, override=True)

    def y(self):
        """Apply y offset for dialogs."""

        y = super(SubstanceWindow, self).y()
        if self.dialog():
            return y - 30
        return y

    def floating(self):
        """Determine if the window is floating."""

        if self.dockable():
            return self.parent().parent().isFloating()
        return True

    def setDocked(self, docked):
        """Change the dock state."""

        if self.dockable():
            self.parent().parent().setFloating(not docked)

    def setWindowPalette(self, program, version=None, style=True, force=False):
        """Set the palette of the window.
        This doesn't seem to do anything so it's disabled by default.
        The force parameter can be set to override this behaviour.
        """

        if force:
            super(SubstanceWindow, self).setWindowPalette(program, version, style)

    def saveWindowPosition(self):
        """Save the window location."""

        if 'substance' not in self.windowSettings:
            self.windowSettings['substance'] = {}
        settings = self.windowSettings['substance']
        substanceSettings['docked'] = self.dockable(raw=True)

        # Save docked settings
        if self.dockable():
            if 'dock' not in settings:
                settings['dock'] = {}

        # Save standalone / dialog settings
        else:
            key = self._getSettingsKey()
            if key not in settings:
                settings[key] = {}

            settings[key]['width'] = self.width()
            settings[key]['height'] = self.height()
            settings[key]['x'] = self.x()
            settings[key]['y'] = self.y()

        super(SubstanceWindow, self).saveWindowPosition()

    def loadWindowPosition(self):
        """Set the position of the window when loaded."""

        if self.dockable():
            return

        key = self._getSettingsKey()
        try:
            width = self.windowSettings['substance'][key]['width']
            height = self.windowSettings['substance'][key]['height']
            x = self.windowSettings['substance'][key]['x']
            y = self.windowSettings['substance'][key]['y']
        except KeyError:
            super(SubstanceWindow, self).loadWindowPosition()
        else:
            x, y = setCoordinatesToScreen(x, y, width, height, padding=5)
            self.resize(width, height)
            self.move(x, y)

    def centreWindow(self, *args, **kwargs):
        """The dialog is already centered so skip."""

        if not self.dialog():
            return super(SubstanceWindow, self).centreWindow(*args, **kwargs)

    def closeEvent(self, event):
        """Catch close events.
        This only triggers with standalone windows.
        """

        if not self.dockable():
            self.saveWindowPosition()
        return super(SubstanceWindow, self).closeEvent(event)

    @classmethod
    def clearWindowInstance(cls, windowID):
        """Close the last class instance."""

        try:
            previousInstance = super(SubstanceWindow, cls).clearWindowInstance(windowID)
        except TypeError:
            return
        if previousInstance is None:
            return

        #Shut down the window
        if not previousInstance['window'].isClosed():
            try:
                previousInstance['window'].close()
            except (RuntimeError, ReferenceError):
                pass

    '''
    def closeEvent(self, event):
        """If the window is dockable, delete the dock widget.
        Currently disabled as it needs to be unregistered too.
        """
        if self.dockable():
            return self.parent().parent().deleteLater()
        return super(SubstanceWindow, self).closeEvent(event)
    '''

    def _parentOverride(self):
        if self.dockable():
            return self.parent().parent()
        return super(SubstanceWindow, self)._parentOverride()

    def isVisible(self):
        """Return if the window is visible."""

        return self._parentOverride().isVisible()

    def setVisible(self, visible):
        """Set if the window is visible."""

        if self.isInstance():
            return super(SubstanceWindow, self).setVisible(visible)
        return self._parentOverride().setVisible(visible)

    def hide(self):
        """Hide the window."""

        return self._parentOverride().hide()

    @hybridmethod
    def show(cls, self, *args, **kwargs):
        """Show the window."""

        # Window is already initialised
        if self is not cls:
            return self._parentOverride().show()

        # Close down window if it exists and open a new one
        try:
            cls.clearWindowInstance(cls.WindowID)
        except AttributeError:
            settings = {}
        else:
            settings = getWindowSettings(cls.WindowID)

        if getattr(cls, 'ForceDialog', False):
            title = getattr(cls, 'WindowName', 'New Window')
            try:
                return dialogWrap(cls, title=title, *args, **kwargs)
            finally:
                cls.clearWindowInstance(cls.WindowID)

        if hasattr(cls, 'WindowDockable'):
            docked = cls.WindowDockable
        else:
            try:
                docked = settings['substance']['docked']
            except KeyError:
                try:
                    docked = cls.WindowDefaults['docked']
                except (AttributeError, KeyError):
                    docked = False

        #Load settings
        try:
            substanceSettings = settings['substance']
        except KeyError:
            substanceSettings = settings['substance'] = {}

        if docked:
            return dockWrap(cls, *args, **kwargs)

        return super(SubstanceWindow, cls).show(*args, **kwargs)
