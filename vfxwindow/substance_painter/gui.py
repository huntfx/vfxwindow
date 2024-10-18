"""Window class for Substance Painter.

Issues:
    Opening a new window with the old one already open will result in a warning:
        [Application] Duplicates found in dock widget object names: `<window>`.
        There will be issues in UI layout save and restore.
"""

from __future__ import absolute_import

from functools import partial
import uuid
from Qt import QtCore, QtWidgets

import substance_painter

from .application import Application
from .callbacks import SubstancePainterCallbacks
from ..abstract.gui import AbstractWindow
from ..utils import setCoordinatesToScreen, hybridmethod, getWindowSettings


def getMainWindow():
    """Get the main application window."""
    return substance_painter.ui.get_main_window()


def dockWrap(windowClass, *args, **kwargs):
    """Create a docked window.
    This can only create it on the first run, afterwards the window
    must be relaunched from the menu.
    """
    class WindowClass(windowClass):
        # Set window ID if needed but disable saving
        if not hasattr(windowClass, 'WindowID'):
            windowClass.WindowID = uuid.uuid4().hex
            def enableSaveWindowPosition(self, enable):
                return super(WindowClass, self).enableSaveWindowPosition(False)

    # Create window
    #WATCHME: Giving the window class a dummy dock widget prevent issues during on init resizing or any method
    # accessing `self.parent()` as it's not a QDockWidget yet (Will be done with the substance `add_dock_widget` function).
    windowInstance = WindowClass(parent=QtWidgets.QDockWidget(getMainWindow()), dockable=True, *args, **kwargs)
    dockWidget = substance_painter.ui.add_dock_widget(windowInstance)
    dockWidget.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    @QtCore.Slot()
    def moveToScreen():
        """Ensure the window doesn't start off screen."""
        if not windowInstance.floating():
            return
        x, y = setCoordinatesToScreen(windowInstance.x(), windowInstance.y(), windowInstance.width(), windowInstance.height(), padding=5)
        windowInstance.move(x, y)

    windowInstance.show()
    windowInstance.windowReady.connect(moveToScreen)
    windowInstance.deferred(windowInstance.windowReady.emit)
    return windowInstance


class SubstancePainterWindow(AbstractWindow):
    """Window to use for Substance Painter."""

    def __init__(self, parent=None, dockable=False, **kwargs):
        if parent is None:
            parent = getMainWindow()
        super(SubstancePainterWindow, self).__init__(parent, **kwargs)

        self._isHiddenSP = False
        self.setDockable(dockable, override=True)

    def _createCallbackHandler(self):
        """Create the callback handler."""
        return SubstancePainterCallbacks(self)

    @property
    def application(self):
        """Get the current application."""
        return Application

    def deferred(self, func, *args, **kwargs):
        """Execute a deferred command."""
        substance_painter.project.execute_when_not_busy(partial(func, *args, **kwargs))

    def move(self, x, y=None):
        if self.docked() and not self.floating():
            return
        return super(SubstancePainterWindow, self).move(x, y)

    def resize(self, width, height=None):
        """Resize the window."""
        if self.docked() and not self.floating():
            return
        return super(SubstancePainterWindow, self).resize(width, height)

    def floating(self):
        """Determine if the window is floating."""
        if self.dockable():
            return self.parent().isFloating()
        return True

    def setDocked(self, docked):
        """Change the dock state."""
        if self.dockable():
            self.parent().setFloating(not docked)

    def setWindowPalette(self, program, version=None, style=True, force=False):
        """Set the palette of the window.
        This doesn't seem to do anything so it's disabled by default.
        The force parameter can be set to override this behaviour.
        """
        if force:
            super(SubstancePainterWindow, self).setWindowPalette(program, version, style)

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

        super(SubstancePainterWindow, self).saveWindowPosition()

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
            super(SubstancePainterWindow, self).loadWindowPosition()
        else:
            x, y = setCoordinatesToScreen(x, y, width, height, padding=5)
            self.resize(width, height)
            self.move(x, y)

    def centreWindow(self, *args, **kwargs):
        """The dialog is already centered so skip."""
        if not self.isDialog():
            return super(SubstancePainterWindow, self).centreWindow(*args, **kwargs)

    def hideEvent(self, event):
        """Unregister callbacks and save window location."""
        if not event.spontaneous() and not self.isClosed():
            self._isHiddenSP = True
            self.callbacks.unregister()
            self.saveWindowPosition()
        return super(SubstancePainterWindow, self).hideEvent(event)

    def showEvent(self, event):
        """Register callbacks and update UI (if checkForChanges is defined)."""
        if not event.spontaneous():
            self._isHiddenSP = False
            self.callbacks.register()
            if hasattr(self, 'checkForChanges'):
                self.checkForChanges()
        return super(SubstancePainterWindow, self).showEvent(event)

    @classmethod
    def clearWindowInstance(cls, windowID):
        """Close the last class instance."""
        try:
            inst = super(SubstancePainterWindow, cls).clearWindowInstance(windowID)
        except TypeError:
            return
        if inst is None:
            return
        inst['window'].callbacks.unregister()

        #Shut down the window
        if not inst['window'].isClosed():
            try:
                inst['window'].close()
            except (RuntimeError, ReferenceError):
                pass

    def closeEvent(self, event):
        """Special case for closing docked windows."""
        if self.dockable():
            self.parent().close()
        else:
            self.saveWindowPosition()
        return super(SubstancePainterWindow, self).closeEvent(event)

    def _parentOverride(self):
        if self.dockable():
            return self.parent()
        return super(SubstancePainterWindow, self)._parentOverride()

    def isVisible(self):
        """Return if the window is visible."""
        if not self.isLoaded() or self.isInstance():
            return super(SubstancePainterWindow, self).isVisible()
        return self._parentOverride().isVisible()

    def setVisible(self, visible):
        """Set if the window is visible."""
        if not self.isLoaded() or self.isInstance():
            return super(SubstancePainterWindow, self).setVisible(visible)
        return self._parentOverride().setVisible(visible)

    def hide(self):
        """Hide the window."""
        if not self.isLoaded() or self.isInstance():
            return super(SubstancePainterWindow, self).hide()
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

        #Load settings
        try:
            substanceSettings = settings[self.application]
        except KeyError:
            substanceSettings = settings[self.application] = {}

        if hasattr(cls, 'WindowDockable'):
            docked = cls.WindowDockable
        else:
            try:
                docked = substanceSettings['docked']
            except KeyError:
                try:
                    docked = cls.WindowDefaults['docked']
                except (AttributeError, KeyError):
                    docked = False

        if docked:
            return dockWrap(cls, *args, **kwargs)

        return super(SubstancePainterWindow, cls).show(*args, **kwargs)

    @classmethod
    def dialog(cls, parent=None, *args, **kwargs):
        """Create the window as a dialog."""
        if parent is None:
            parent = getMainWindow()
        return super(SubstancePainterWindow, cls).dialog(parent=parent, *args, **kwargs)
