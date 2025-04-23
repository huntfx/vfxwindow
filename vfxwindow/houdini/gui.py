"""Window class for Houdini."""

from __future__ import absolute_import

import hou
import hdefereval

from Qt import QtCore

from .application import Application
from .callbacks import HoudiniCallbacks
from ..abstract.gui import AbstractWindow
from ..utils import setCoordinatesToScreen, deprecate


def getMainWindow():
    """Get an instance of the main window."""
    return hou.ui.mainQtWindow()


def getStyleSheet():
    """Get the Houdini stylesheet, possibly for use outside the program.
    For inside Houdini, use setProperty('houdiniStyle', True).
    """
    return hou.qt.styleSheet()


class HoudiniWindow(AbstractWindow):
    """Window to use for Houdini.
    This also performs some necessary CSS edits to fix colours.
    """

    def __init__(self, parent=None, **kwargs):
        if parent is None:
            parent = getMainWindow()
        super(HoudiniWindow, self).__init__(parent, **kwargs)

        # Fix some issues with widgets not taking the correct style
        self.setStyleSheet("""
            QScrollArea{
                background: rgb(58, 58, 58);
                border: none;
            }
            QTreeWidget{
                background: rgb(43, 43, 43);
                border: none;
                alternate-background-color: rgb(170, 70, 70);
            }
            QProgressBar{
                color: rgb(0, 0, 0);
            }""")
        self.setProperty('houdiniStyle', True)

        # As of today, that's the only solution that seems to make this window stay over houdini.
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Dialog)

    def _createCallbackHandler(self):
        """Create the callback handler."""
        return HoudiniCallbacks(self)

    @property
    def application(self):
        """Get the current application."""
        return Application

    def closeEvent(self, event):
        """Save the window location on window close."""
        self.saveWindowPosition()
        self.clearWindowInstance(self.WindowID)
        return super(HoudiniWindow, self).closeEvent(event)

    @deprecate
    def displayMessage(self, message):
        """Show a popup message."""
        hou.ui.displayMessage(message)

    def windowPalette(self):
        currentPalette = super(HoudiniWindow, self).windowPalette()
        if currentPalette is None:
            return 'Houdini.{}'.format(int(self.application.version))
        return currentPalette

    def saveWindowPosition(self):
        """Save the window location."""
        if self.application in self.windowSettings:
            settings = self.windowSettings[self.application]
        else:
            settings = self.windowSettings[self.application] = {}

        key = self._getSettingsKey()
        if key not in settings:
            settings[key] = {}

        settings[key]['width'] = self.width()
        settings[key]['height'] = self.height()
        settings[key]['x'] = self.x()
        settings[key]['y'] = self.y()

        super(HoudiniWindow, self).saveWindowPosition()

    def loadWindowPosition(self):
        """Set the position of the window when loaded."""
        try:
            settings = self.windowSettings[self.application][self._getSettingsKey()]
            x = settings['x']
            y = settings['y']
            width = settings['width']
            height = settings['height']
        except KeyError:
            super(HoudiniWindow, self).loadWindowPosition()
        else:
            x, y = setCoordinatesToScreen(x, y, width, height, padding=5)
            self.resize(width, height)
            self.move(x, y)

    @classmethod
    def dialog(cls, parent=None, *args, **kwargs):
        """Create the window as a dialog."""
        if parent is None:
            parent = getMainWindow()
        return super(HoudiniWindow, cls).dialog(parent=parent, *args, **kwargs)

    @classmethod
    def clearWindowInstance(self, windowID):
        """Close the last class instance."""
        previousInstance = super(HoudiniWindow, self).clearWindowInstance(windowID)
        if previousInstance is None:
            return

        #Shut down the window
        if not previousInstance['window'].isClosed():
            try:
                previousInstance['window'].close()
            except (RuntimeError, ReferenceError):
                pass

    def deferred(self, func, *args, **kwargs):
        """Defer function until Houdini is ready."""
        hdefereval.executeDeferred(func, *args, **kwargs)
