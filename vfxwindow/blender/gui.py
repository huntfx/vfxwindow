"""Window class for Blender."""

from __future__ import absolute_import

from collections import defaultdict
from functools import partial

import bpy

from .application import Application
from .callbacks import BlenderCallbacks
from ..utils import setCoordinatesToScreen, hybridmethod
from ..standalone.gui import StandaloneWindow


class BlenderWindow(StandaloneWindow):
    """Window to use for Blender."""

    CallbackClass = BlenderCallbacks

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

        super(BlenderWindow, self).saveWindowPosition()

    @property
    def application(self):
        """Get the current application."""
        return Application

    def deferred(self, func, *args, **kwargs):
        """Defer the execution of a function."""
        def noReturn():
            """Execute without a return value.

            The timer uses return values to determine when to next run
            the function, so skipping it ensures it's only run once.
            """
            func(*args, **kwargs)
        bpy.app.timers.register(noReturn, first_interval=0)

    def loadWindowPosition(self):
        """Set the position of the window when loaded."""
        try:
            settings = self.windowSettings[self.application][self._getSettingsKey()]
            x = settings['x']
            y = settings['y']
            width = settings['width']
            height = settings['height']
        except KeyError:
            super(BlenderWindow, self).loadWindowPosition()
        else:
            x, y = setCoordinatesToScreen(x, y, width, height, padding=5)
            self.resize(width, height)
            self.move(x, y)

    @hybridmethod
    def show(cls, self, *args, **kwargs):
        """Show the Blender window."""
        # Window is already initialised
        if self is not cls:
            return super(BlenderWindow, self).show()

        # Close down window if it exists and open a new one
        try:
            cls.clearWindowInstance(cls.ID)
        except AttributeError:
            pass
        kwargs['init'] = not bpy.app.background
        kwargs['instance'] = True
        kwargs['exec_'] = bpy.app.background
        return super(BlenderWindow, cls).show(*args, **kwargs)

    @classmethod
    def clearWindowInstance(cls, windowID):
        """Close the last class instance."""
        inst = super(BlenderWindow, cls).clearWindowInstance(windowID)

        if inst is not None:
            inst['window'].callbacks.unregister()

        return inst
