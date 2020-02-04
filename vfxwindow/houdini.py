"""Window class for Houdini."""

from __future__ import absolute_import

import hou
import hdefereval

from .abstract import AbstractWindow
from .utils import setCoordinatesToScreen


HOUDINI_VERSION = hou.applicationVersion()[0]


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
    It has support for automatically saving the position when closed,
    and performs some necessary CSS edits to fix colours.
    """
    def __init__(self, parent=None, **kwargs):
        if parent is None:
            parent = getMainWindow()
        super(HoudiniWindow, self).__init__(parent, **kwargs)
        self.houdini = True

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

    def closeEvent(self, event):
        """Save the window location on window close."""
        self.saveWindowPosition()
        self.clearWindowInstance(self.WindowID)
        return super(HoudiniWindow, self).closeEvent(event)

    def displayMessage(self, message):
        """Show a popup message."""
        hou.ui.displayMessage(message)

    def windowPalette(self):
        currentPalette = super(HoudiniWindow, self).windowPalette()
        if currentPalette is None:
            return 'Houdini.{}'.format(HOUDINI_VERSION)
        return currentPalette

    def saveWindowPosition(self):
        """Save the window location."""
        try:
            houdiniSettings = self.windowSettings['houdini']
        except KeyError:
            houdiniSettings = self.windowSettings['houdini'] = {}
        try:
            mainWindowSettings = houdiniSettings['main']
        except KeyError:
            mainWindowSettings = houdiniSettings['main'] = {}

        mainWindowSettings['width'] = self.width()
        mainWindowSettings['height'] = self.height()
        mainWindowSettings['x'] = self.x()
        mainWindowSettings['y'] = self.y()
        super(HoudiniWindow, self).saveWindowPosition()

    def loadWindowPosition(self):
        """Set the position of the window when loaded."""
        try:
            x = self.windowSettings['houdini']['main']['x']
            y = self.windowSettings['houdini']['main']['y']
            width = self.windowSettings['houdini']['main']['width']
            height = self.windowSettings['houdini']['main']['height']
        except KeyError:
            super(HoudiniWindow, self).loadWindowPosition()
        else:
            x, y = setCoordinatesToScreen(x, y, width, height, padding=5)
            self.resize(width, height)
            self.move(x, y)

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
        hdefereval.executeDeferred(func, *args, **kwargs)
