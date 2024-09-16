"""Window class for Katana."""

from __future__ import absolute_import, print_function

from Qt import QtWidgets, QtCore

from Katana import UI4

from .application import Application
from ..abstract.gui import AbstractWindow
from ..utils import hybridmethod, setCoordinatesToScreen


def getMainWindow():
    """Returns the main window."""
    return UI4.App.MainWindow.GetMainWindow()


class KatanaWindow(AbstractWindow):
    """Window to use for Katana."""

    def __init__(self, parent=None, **kwargs):
        if parent is None:
            parent = getMainWindow()
        super(KatanaWindow, self).__init__(parent, **kwargs)
        self.installEventFilter(self)
        self.destroyed.connect(self.onDestroy)

    def eventFilter(self, obj, event):
        print(event)
        return super(KatanaWindow, self).eventFilter(obj, event)

    @QtCore.Slot()
    def onDestroy(self):
        print('destroyed')

    @property
    def application(self):
        """Get the current application."""
        return Application

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

        super(KatanaWindow, self).saveWindowPosition()

    def loadWindowPosition(self):
        """Set the position of the window when loaded."""
        try:
            settings = self.windowSettings[self.application][self._getSettingsKey()]
            width = settings['width']
            height = settings['height']
            x = settings['x']
            y = settings['y']
        except KeyError:
            super(KatanaWindow, self).loadWindowPosition()
        else:
            x, y = setCoordinatesToScreen(x, y, width, height, padding=5)
            self.resize(width, height)
            self.move(x, y)

    def setWindowPalette(self, program, version=None, style=True, force=False):
        """Set the palette of the window.
        This affects the entire Katana GUI so it's disabled by default.
        The force parameter can be set to override this behaviour.
        """
        if force:
            super(KatanaWindow, self).setWindowPalette(program, version, style)

    def windowPalette(self):
        """Get the current window palette."""
        print('WINDOWPALETTE')
        currentPalette = super(KatanaWindow, self).windowPalette()
        if currentPalette is None:
            return 'Katana.{}'.format(int(self.application.version))
        return currentPalette

    @hybridmethod
    def show(cls, self, *args, **kwargs):
        """Show the Katana window."""
        print('SHOW')
        # Window is already initialised
        if self is not cls:
            return super(KatanaWindow, self).show()

        # Close down window if it exists and open a new one
        try:
            cls.clearWindowInstance(cls.WindowID)
        except AttributeError:
            pass
        return super(KatanaWindow, cls).show(*args, **kwargs)

    def closeEvent(self, event):
        """Save the position before closing."""
        print('CLOSEEVENT')
        self.saveWindowPosition()
        return super(KatanaWindow, self).closeEvent(event)

    def hideEvent(self, event):
        """Save the position before closing."""
        print('HIDEEVENT')
        return super(KatanaWindow, self).hideEvent(event)

    def showEvent(self, event):
        """Save the position before closing."""
        print('SHOWEVENT')
        return super(KatanaWindow, self).showEvent(event)
