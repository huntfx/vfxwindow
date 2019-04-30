"""Window class for Unreal.

WARNING: THIS IS NOT EVEN TESTED AND WILL NOT WORK, JUST PUTTING CODE HERE FOR LATER
"""

from __future__ import absolute_import

import unreal

from .base import QBaseWindow


VERSION = 4


def dockWrapper(windowClass, dock=True, resetFloating=True):
    """Dock a Qt widget inside Unreal Engine.

    Source: https://forums.unrealengine.com/unreal-engine/unreal-studio/1526501-how-to-get-the-main-window-of-the-editor-to-parent-qt-or-pyside-application-to-it
    """
    windowInstance = windowClass()
    unreal.parent_external_window_to_slate(windowInstance.winId())

    try:
        windowInstance.loadWindowPosition()
    except (AttributeError, TypeError):
        pass
    return windowInstance


class UnrealWindow(QBaseWindow):

    def __init__(self, parent=None, dockable=False):
        super(UnrealWindow, self).__init__(parent)
        self.unreal = True
        self.setDockable(dockable, override=True)

    def closeEvent(self, event):
        """Save the window location on window close."""
        self.saveWindowPosition()
        self.clearWindowInstance(self.ID)
        return super(UnrealWindow, self).closeEvent(event)

    def windowPalette(self):
        currentPalette = super(UnrealWindow, self).windowPalette()
        if currentPalette is None:
            return 'Unreal.{}'.format(VERSION)
        return currentPalette

    def saveWindowPosition(self):
        """Save the window location."""
        if self.dockable():
            try:
                dockWindowSettings = self.windowSettings['unreal']['dock']
            except KeyError:
                dockWindowSettings = self.windowSettings['unreal']['dock'] = {}
            dockWindowSettings['width'] = self.width()
            dockWindowSettings['height'] = self.height()
            dockWindowSettings['x'] = self.x()
            dockWindowSettings['y'] = self.y()
        else:
            try:
                mainWindowSettings = self.windowSettings['unreal']['main']
            except KeyError:
                mainWindowSettings = self.windowSettings['unreal']['main'] = {}
            mainWindowSettings['width'] = self.width()
            mainWindowSettings['height'] = self.height()
            mainWindowSettings['x'] = self.x()
            mainWindowSettings['y'] = self.y()

        super(UnrealWindow, self).saveWindowPosition()

    def loadWindowPosition(self):
        """Set the position of the window when loaded."""
        try:
            width = self.windowSettings['unreal']['main']['width']
            height = self.windowSettings['unreal']['main']['height']
            x = self.windowSettings['unreal']['main']['x']
            y = self.windowSettings['unreal']['main']['y']
        except KeyError:
            super(UnrealWindow, self).loadWindowPosition()
        else:
            self.resize(width, height)
            self.move(x, y)

    @classmethod
    def clearWindowInstance(self, windowID):
        """Close the last class instance."""
        previousInstance = super(UnrealWindow, self).clearWindowInstance(windowID)
        if previousInstance is None:
            return

        #Shut down the window
        if not previousInstance['window'].isClosed():
            try:
                previousInstance['window'].close()
            except (RuntimeError, ReferenceError):
                pass

    @classmethod
    def show(cls, **kwargs):
        #Close down any instances of the window
        try:
            cls.clearWindowInstance(cls.ID)
        except AttributeError:
            settings = {}
        else:
            settings = cls.getWindowSettings(cls.ID)

        #Load settings
        try:
            unrealSettings = settings['unreal']
        except KeyError:
            unrealSettings = settings['unreal'] = {}
        try:
            is_docked = unrealSettings['docked']
        except KeyError:
            try:
                is_docked = cls.DEFAULTS['docked']
            except (AttributeError, KeyError):
                is_docked = True

        #Return new class instance and show window
        if is_docked:
            return dockWrapper(cls)

        return super(UnrealWindow, cls).show()
