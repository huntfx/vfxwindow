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

import uuid
from Qt import QtCore, QtWidgets

import sd

from .application import Application
from ..abstract.gui import AbstractWindow
from ..utils import setCoordinatesToScreen, hybridmethod, getWindowSettings


APPLICATION = sd.getContext().getSDApplication()

MANAGER = APPLICATION.getQtForPythonUIMgr()


def getMainWindow():
    """Get the main application window."""
    return MANAGER.getMainWindow()


def dockWrap(windowClass, *args, **kwargs):
    """Create a docked window.
    This can only create it on the first run, afterwards the window
    must be relaunched from the menu.
    """
    class WindowClass(windowClass):
        # Set window ID if needed but disable saving
        if not getattr(windowClass, 'WindowID', None):
            windowClass.WindowID = uuid.uuid4().hex
            def enableSaveWindowPosition(self, enable):
                return super(WindowClass, self).enableSaveWindowPosition(False)

    # Create layout
    layout = QtWidgets.QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)

    # Create dock
    dock = MANAGER.newDockWidget(identifier=WindowClass.WindowID, title=getattr(WindowClass, 'WindowName', 'New Window'))
    dock.setLayout(layout)
    dockWidget = dock.parent()
    dockWidget.show()

    @QtCore.Slot()
    def moveToScreen():
        """Ensure the window doesn't start off screen."""
        if not windowInstance.floating():
            return
        x, y = setCoordinatesToScreen(windowInstance.x(), windowInstance.y(), windowInstance.width(),
                                      windowInstance.height(), padding=5)
        windowInstance.move(x, y)

    # Create window
    windowInstance = WindowClass(parent=dockWidget, dockable=True, *args, **kwargs)
    layout.addWidget(windowInstance)
    windowInstance.windowReady.connect(moveToScreen)
    windowInstance.deferred(windowInstance.windowReady.emit)
    return windowInstance


class SubstanceDesignerWindow(AbstractWindow):
    """Window to use for Substance Designer."""

    def __init__(self, parent=None, dockable=False, **kwargs):
        if dockable:
            self._sdParent, parent = parent, None
        elif parent is None:
            parent = getMainWindow()
        super(SubstanceDesignerWindow, self).__init__(parent, **kwargs)

        self.setDockable(dockable, override=True)

    @property
    def application(self):
        """Get the current application."""
        return Application

    def y(self):
        """Apply y offset for dialogs."""
        y = super(SubstanceDesignerWindow, self).y()
        if self.isDialog():
            return y - 30
        return y

    def move(self, x, y=None):
        if self.docked() and not self.floating():
            return
        return super(SubstanceDesignerWindow, self).move(x, y)

    def resize(self, width, height=None):
        """Resize the window."""
        if self.docked() and not self.floating():
            return
        return super(SubstanceDesignerWindow, self).resize(width, height)

    def floating(self):
        """Determine if the window is floating."""
        if self.dockable():
            return self._parentOverride().isFloating()
        return True

    def setDocked(self, docked):
        """Change the dock state."""
        if self.dockable():
            self._parentOverride().setFloating(not docked)

    def setWindowPalette(self, program, version=None, style=True, force=False):
        """Set the palette of the window.
        This doesn't seem to do anything so it's disabled by default.
        The force parameter can be set to override this behaviour.
        """
        if force:
            super(SubstanceDesignerWindow, self).setWindowPalette(program, version, style)

    def saveWindowPosition(self):
        """Save the window location."""
        if self.application in self.windowSettings:
            settings = self.windowSettings[self.application]
        else:
            settings = self.windowSettings[self.application] = {}

        settings['docked'] = self.dockable(raw=True)

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

        super(SubstanceDesignerWindow, self).saveWindowPosition()

    def loadWindowPosition(self):
        """Set the position of the window when loaded."""
        if self.dockable():
            return

        try:
            settings = self.windowSettings[self.application][self._getSettingsKey()]
            width = settings['width']
            height = settings['height']
            x = settings['x']
            y = settings['y']
        except KeyError:
            super(SubstanceDesignerWindow, self).loadWindowPosition()
        else:
            x, y = setCoordinatesToScreen(x, y, width, height, padding=5)
            self.resize(width, height)
            self.move(x, y)

    def centreWindow(self, *args, **kwargs):
        """The dialog is already centered so skip."""
        if not self.isDialog():
            return super(SubstanceDesignerWindow, self).centreWindow(*args, **kwargs)

    def closeEvent(self, event):
        """Catch close events.
        This only triggers with standalone windows.
        """
        if not self.dockable():
            self.saveWindowPosition()
        return super(SubstanceDesignerWindow, self).closeEvent(event)

    @classmethod
    def clearWindowInstance(cls, windowID):
        """Close the last class instance."""
        try:
            previousInstance = super(SubstanceDesignerWindow, cls).clearWindowInstance(windowID)
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

    def _parentOverride(self):
        if self.dockable():
            return self._sdParent
        return super(SubstanceDesignerWindow, self)._parentOverride()

    def isVisible(self):
        """Return if the window is visible."""
        return self._parentOverride().isVisible()

    def setVisible(self, visible):
        """Set if the window is visible."""
        if self.isInstance() or not self.isLoaded():
            return super(SubstanceDesignerWindow, self).setVisible(visible)
        return self._parentOverride().setVisible(visible)

    def hide(self):
        """Hide the window."""
        return self._parentOverride().hide()

    def deferred(self, func, *args, **kwargs):
        """Defer a function execution by 1 second.
        Substance has no better alternative currently.
        """
        QtCore.QTimer.singleShot(1000, func)

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

        if hasattr(cls, 'WindowDockable'):
            docked = cls.WindowDockable
        else:
            try:
                docked = settings[self.application]['docked']
            except KeyError:
                try:
                    docked = cls.WindowDefaults['docked']
                except (AttributeError, KeyError):
                    docked = False

        #Load settings
        try:
            substanceSettings = settings[self.application]
        except KeyError:
            substanceSettings = settings[self.application] = {}

        if docked:
            return dockWrap(cls, *args, **kwargs)

        return super(SubstanceDesignerWindow, cls).show(*args, **kwargs)

    @classmethod
    def dialog(cls, parent=None, *args, **kwargs):
        """Create the window as a dialog."""
        if parent is None:
            parent = getMainWindow()
        return super(SubstanceDesignerWindow, cls).dialog(parent=parent, *args, **kwargs)
