"""Window class for Blender."""

from __future__ import absolute_import

import sys
from collections import defaultdict
from Qt import QtWidgets

import bpy

from .utils import setCoordinatesToScreen, hybridmethod
from .standalone import StandaloneWindow


VERSION = bpy.app.version_string


class BlenderWindow(StandaloneWindow):
    """Window to use for Blender."""

    def __init__(self, parent=None, **kwargs):
        super(BlenderWindow, self).__init__(parent, **kwargs)
        
        self.blender = True  #: .. deprecated:: 1.9.0 Use :property:`~AbstractWindow.software` instead.
        self.standalone = False  #: .. deprecated:: 1.9.0 Won't be needed anymore when using :property:`~AbstractWindow.software`.

    @property
    def software(self):
        return 'Blender'

    def saveWindowPosition(self):
        """Save the window location."""
        if self.software not in self.windowSettings:
            self.windowSettings[self.software] = {}
        settings = self.windowSettings[self.software]

        key = self._getSettingsKey()
        if key not in settings:
            settings[key] = {}

        settings[key]['width'] = self.width()
        settings[key]['height'] = self.height()
        settings[key]['x'] = self.x()
        settings[key]['y'] = self.y()

        super(BlenderWindow, self).saveWindowPosition()

    def loadWindowPosition(self):
        """Set the position of the window when loaded."""
        key = self._getSettingsKey()
        try:
            x = self.windowSettings[self.software][key]['x']
            y = self.windowSettings[self.software][key]['y']
            width = self.windowSettings[self.software][key]['width']
            height = self.windowSettings[self.software][key]['height']
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
        kwargs['instance'] = True
        kwargs['exec_'] = False
        return super(BlenderWindow, cls).show(*args, **kwargs)

    @hybridmethod
    def removeCallbacks(cls, self, group=None, windowInstance=None, windowID=None):
        """Remove all the registered callbacks.
        If group is not set, then all will be removed.

        Either windowInstance or windowID is needed if calling without a class instance.
        """
        # Handle classmethod
        if self is cls:
            if windowInstance is None and windowID is not None:
                windowInstance = cls.windowInstance(windowID)
            if windowInstance is None:
                raise ValueError('windowInstance or windowID parameter is required for classmethod')
        # Handle normal method
        elif windowInstance is None:
            windowInstance = self.windowInstance()

        # Select all groups if specific one not provided
        if group is None:
            groups = list(windowInstance['callback'].keys())
        else:
            if group not in windowInstance['callback']:
                return 0
            groups = [group]

        numEvents = 0
        for group in groups:
            for callback_attr, callbacks in windowInstance['callback'][group].items():
                callback_list = getattr(bpy.app.handlers, callback_attr)
                for func in callbacks:
                    callback_list.remove(func)
                    numEvents += 1
            del windowInstance['callback'][group]
        return numEvents

    def _addBlenderCallbackGroup(self, group):
        """Add a callback group."""
        windowInstance = self.windowInstance()
        if group in windowInstance['callback']:
            return
        windowInstance['callback'][group] = defaultdict(list)

    def _addApplicationHandler(self, handler, func, persistent=True, group=None):
        """Add an application handler.

        See Also:
            https://docs.blender.org/api/2.79/bpy.app.handlers.html
        """
        self._addBlenderCallbackGroup(group)

        # Persistent handlers appear to just have the _bpy_persistent attribute added
        isPersistent = hasattr(func, '_bpy_persistent')
        if persistent and not isPersistent:
            func = bpy.app.handlers.persistent(func)
        elif not persistent and isPersistent:
            del func._bpy_persistent

        # Add the function to the handler
        getattr(bpy.app.handlers, handler).append(func)
        self.windowInstance()['callback'][group][handler].append(func)

    def addCallbackFrameChangeAfter(self, func, persistent=True, group=None):
        """After frame change for playback and rendering."""
        self._addApplicationHandler('frame_change_post', func, persistent=persistent, group=group)

    def addCallbackFrameChangeBefore(self, func, persistent=True, group=None):
        """Before frame change for playback and rendering."""
        self._addApplicationHandler('frame_change_pre', func, persistent=persistent, group=group)

    def addCallbackGameAfter(self, func, persistent=True, group=None):
        """On ending the game engine."""
        self._addApplicationHandler('game_post', func, persistent=persistent, group=group)

    def addCallbackGameBefore(self, func, persistent=True, group=None):
        """On starting the game engine."""
        self._addApplicationHandler('game_pre', func, persistent=persistent, group=group)

    def addCallbackLoadSceneAfter(self, func, persistent=True, group=None):
        """After loading a new blend file."""
        self._addApplicationHandler('load_post', func, persistent=persistent, group=group)

    def addCallbackLoadSceneBefore(self, func, persistent=True, group=None):
        """After loading a new blend file."""
        self._addApplicationHandler('load_pre', func, persistent=persistent, group=group)

    def addCallbackRenderCancel(self, func, persistent=True, group=None):
        """On canceling a render job."""
        self._addApplicationHandler('render_cancel', func, persistent=persistent, group=group)

    def addCallbackRenderComplete(self, func, persistent=True, group=None):
        """On completion of render job."""
        self._addApplicationHandler('render_complete', func, persistent=persistent, group=group)

    def addCallbackRenderInit(self, func, persistent=True, group=None):
        """On initialisation of a render job."""
        self._addApplicationHandler('render_init', func, persistent=persistent, group=group)

    def addCallbackRenderAfter(self, func, persistent=True, group=None):
        """After rendering."""
        self._addApplicationHandler('render_post', func, persistent=persistent, group=group)

    def addCallbackRenderBefore(self, func, persistent=True, group=None):
        """Before rendering."""
        self._addApplicationHandler('render_pre', func, persistent=persistent, group=group)

    def addCallbackRenderStats(self, func, persistent=True, group=None):
        """On printing render statistics."""
        self._addApplicationHandler('render_stats', func, persistent=persistent, group=group)

    def addCallbackRenderWrite(self, func, persistent=True, group=None):
        """After writing a rendered frame."""
        self._addApplicationHandler('render_write', func, persistent=persistent, group=group)

    def addCallbackSaveSceneAfter(self, func, persistent=True, group=None):
        """After saving a blend file."""
        self._addApplicationHandler('save_post', func, persistent=persistent, group=group)

    def addCallbackSaveSceneBefore(self, func, persistent=True, group=None):
        """Before saving blend file."""
        self._addApplicationHandler('save_pre', func, persistent=persistent, group=group)

    def addCallbackSceneUpdateAfter(self, func, persistent=True, group=None):
        """After each scene data update.
        It does not necessarily imply that anything has changed.
        Removed in Blender 2.80
        """
        self._addApplicationHandler('scene_update_post', func, persistent=persistent, group=group)

    def addCallbackSceneUpdateBefore(self, func, persistent=True, group=None):
        """After each scene data update.
        It does not necessarily imply that anything has changed.
        Removed in Blender 2.80
        """
        self._addApplicationHandler('scene_update_pre', func, persistent=persistent, group=group)

    def addCallbackVersionUpdate(self, func, persistent=True, group=None):
        """On ending the versioning code."""
        self._addApplicationHandler('version_update', func, persistent=persistent, group=group)

    def addCallbackDepsgraphUpdateAfter(self, func, persistent=True, group=None):
        """After depsgraph update.
        Added in Blender 2.80.
        """
        self._addApplicationHandler('depsgraph_update_post', func, persistent=persistent, group=group)

    def addCallbackDepsgraphUpdateBefore(self, func, persistent=True, group=None):
        """Before depsgraph update.
        Added in Blender 2.80.
        """
        self._addApplicationHandler('depsgraph_update_pre', func, persistent=persistent, group=group)

    def addCallbackUndoAfter(self, func, persistent=True, group=None):
        """After loading an undo step."""
        self._addApplicationHandler('undo_post', func, persistent=persistent, group=group)

    def addCallbackUndoBefore(self, func, persistent=True, group=None):
        """Before loading an undo step."""
        self._addApplicationHandler('undo_pre', func, persistent=persistent, group=group)

    def addCallbackRedoAfter(self, func, persistent=True, group=None):
        """After loading a redo step."""
        self._addApplicationHandler('redo_post', func, persistent=persistent, group=group)

    def addCallbackRedoBefore(self, func, persistent=True, group=None):
        """Before loading a redo step."""
        self._addApplicationHandler('redo_pre', func, persistent=persistent, group=group)
