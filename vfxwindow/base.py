"""Base class for other porgrams to inherit.
This should never be the top window as it contains a few functions that need overrides.
"""

from __future__ import absolute_import

import json
import os
import tempfile
import uuid
from collections import defaultdict

from .palette import setPalette
from .utils import hybridmethod, setCoordinatesToScreen
from .utils.Qt import QtCore, QtWidgets


def getWindowSettingsPath(windowID):
    """Get a path to the window settings."""
    return os.path.join(tempfile.gettempdir(), 'VFXWindow.{}.json'.format(windowID))


def getWindowSettings(windowID, path=None):
    """Load the window settings, or return empty dict if they don't exist."""
    if path is None:
        path = getWindowSettingsPath(windowID)
    try:
        with open(path, 'r') as f:
            return json.loads(f.read())
    except (IOError, ValueError):
        return {}


def saveWindowSettings(windowID, data, path=None):
    """Save the window settings."""
    if path is None:
        path = getWindowSettingsPath(windowID)
    try:
        with open(path, 'w') as f:
            f.write(json.dumps(data, indent=2))
    except IOError:
        return False
    return True


class BaseWindow(QtWidgets.QMainWindow):
    """Base class for all Qt windows.

    Each window must be provided with a unique "ID" attribute to enable the saving and
     loading of its location betweem sessions. This will also enable the automatic closing
     of a previous window if a new one is launched, via the clearWindowInstance methods.
    A "NAME" attribute will determine the window title, or it will revert to "New Window"

    Dockable Windows:
        The dockable attribute should be used if the window can be integrated into a program.
        The _parentOverride method must then be set to supply the correct attributes,
         since self.parent() is likely a wrapper with the incorrect dimensions and location.
        Sometimes this won't be enough, and the attributes must be overridden.

        Overridden Methods:
            floating()
            move(x, y)
            geometry()
            frameGeometry()
            rect()
            width()
            height()
            x()
            y()
            resize(width, height)
    
    Startup Commands:
        setDefaultSize(width, height)       # Set size if settings can't be read
        setDefaultPosition(x, y)            # Set position if settings can't be read
        setWindowPalette(palette)           # Set a palette
    """
    windowReady = QtCore.Signal()
    
    _WINDOW_INSTANCES = {}

    def __init__(self, parent=None, **kwargs):
        super(BaseWindow, self).__init__(parent, **kwargs)
        
        # Setup window attributes and saving
        self.enableSaveWindowPosition(True)
        self.__forceDisableSaving = not hasattr(self, 'ID')
        if self.__forceDisableSaving:
            self.ID = uuid.uuid4()
        self.setWindowTitle(getattr(self, 'NAME', 'New Window'))

        # Track settings that to be read by any inherited windows
        self.maya = False
        self.nuke = False
        self.houdini = False
        self.fusion = False
        self.blender = False
        self.unreal = False
        self.standalone = False

        # Read settings
        self._windowDataPath = getWindowSettingsPath(self.ID)
        tempFolder = os.path.dirname(self._windowDataPath)
        if not os.path.exists(tempFolder):
            os.makedirs(tempFolder)
        self.windowSettings = getWindowSettings(self.ID, path=self._windowDataPath)

        self._signals = defaultdict(list)
        self.__closed = False
        self.__dockable = False
        self.__wasDocked = None
        self.__initialPosOverride = None

        # Store the window data so it can be closed later
        # In some cases such as Maya's layoutDialog, the window will
        # be deleted too early, so we can't use weakref.proxy(self)
        BaseWindow._WINDOW_INSTANCES[self.ID] = {
            'window': self,
            'callback': {}
        }

    def signalExists(self, group):
        """How many signals exist for the given group."""
        return len(self.signal(group) or [])

    def signalDisconnect(self, group):
        """Disconnect and return all functions for a current group.
        If none exist, and empty list will be returned.

        >>> self.signalDisconnect('widget_changed')
        [self.widgetChanged]
        >>> self.signalDisconnect('widget_changed')
        []
        """
        signals = []
        for (signal, func) in self._signals.pop(group, []):
            try:
                signal.disconnect(func)
            except RuntimeError:
                pass
            else:
                signals.append(func)
        return signals

    def signalConnect(self, signal, func, group=None):
        """Add a new signal for the current group.

        >>> self.signalConnect(widget.currentIndexChanged, self.widgetChanged, 'widget_changed')
        """
        self._signals[group].append((signal, func))
        signal.connect(func)
        return func

    def dockable(self, raw=False):
        """Return if the window is dockable.
        
        Parameters:
            raw (bool): If True, get the current state of the window, otherwise get the current
                setting, which may require a reload to apply if changed.
        """
        if hasattr(self, 'DOCKABLE'):
            return self.DOCKABLE
        if not raw and self.__wasDocked is not None:
            return self.__wasDocked
        return self.__dockable

    def setDockable(self, dockable, override=False):
        """Set if the window should be dockable.

        Parameters:
            override (bool): If the dockable raw value should be set too.
                Should only be used if the dock state has changed.
        """
        if override:
            self.__wasDocked = self.__dockable = dockable
        else:
            self.__wasDocked = self.__dockable
            self.__dockable = dockable
            self.saveWindowPosition()

    def docked(self):
        """Return if the window is currently docked."""
        if not self.dockable():
            return False
        return NotImplementedError('override needed')

    def setDocked(self, docked):
        """Force the window to dock or undock."""
        pass
    
    def loadWindowPosition(self):
        """Load the previous position or centre the window.
        The loading must be done in an override.
        """
        if self.__initialPosOverride is not None:
            x, y = self.__initialPosOverride
            x, y = setCoordinatesToScreen(x, y, self.width(), self.height(), padding=5)
            self.move(x, y)
        else:
            self.centreWindow()

    def enableSaveWindowPosition(self, enable):
        """Enable or disable saving the window position."""
        self._enableSave = enable

    def saveWindowPosition(self, path=None):
        """Save the window settings into a file."""
        if self.__forceDisableSaving or not self._enableSave:
            return False
        if path is None:
            path = self._windowDataPath
        return saveWindowSettings(self.ID, self.windowSettings, path=path)

    def displayMessage(self, message, title=None):
        """Display a popup box."""
        notify = QtWidgets.QMessageBox()
        notify.setText(message)
        if title is not None:
            notify.setWindowTitle(title)
        notify.exec_()

    @hybridmethod
    def show(cls, self, parent=None, **kwargs):
        """Show the window and load its position."""
        if self is not cls:
            return super(BaseWindow, self).show()

        try:
            cls.clearWindowInstance(cls.ID)
        except AttributeError:
            pass
        new = cls(parent, **kwargs)
        super(BaseWindow, new).show()
        new.loadWindowPosition()
        new.deferred(new.windowReady.emit)
        return new

    def setDefaultSize(self, width, height):
        """Set a default size upon widget load."""
        self.resize(width, height)

    def setDefaultWidth(self, width):
        """Set a default width upon widget load."""
        self.resize(width, self.height())

    def setDefaultHeight(self, height):
        """Set a default height upon widget load."""
        self.resize(self.width(), height)

    def setDefaultPosition(self, x, y):
        """Set a default position upon widget load."""
        self.__initialPosOverride = (x, y)
    
    @hybridmethod
    def windowInstance(cls, self, windowID=None, delete=False):
        """Get the instance of the current window or one with an ID."""
        if windowID is None:
            if self is cls:
                return
            windowID = self.ID

        if windowID in cls._WINDOW_INSTANCES:
            if delete and self is cls:
                return cls._WINDOW_INSTANCES.pop(windowID)
            return cls._WINDOW_INSTANCES[windowID]

    @classmethod
    def clearWindowInstance(cls, windowID):
        """Close the last class instance.
        This must be subclassed if the window needs to be closed.
        """
        return cls._WINDOW_INSTANCES.pop(windowID, None)

    @classmethod
    def clearWindowInstances(cls):
        """Close down every loaded window."""
        for windowID in tuple(cls._WINDOW_INSTANCES):
            cls.clearWindowInstance(windowID)

    def close(self):
        """Close the window and mark it as closed."""
        self.__closed = True
        super(BaseWindow, self).close()

    def isClosed(self):
        """Return if the window has been closed."""
        return self.__closed
    
    def setWindowPalette(self, program, version=None, style=True):
        """Set the palette of the window."""
        setPalette(program, version, style=style)
        self._windowPalette = program
        if version is not None:
            self._windowPalette += '.{}'.format(version)
    
    def windowPalette(self):
        """Find the current palette of the window."""
        if hasattr(self, '_windowPalette'):
            return self._windowPalette
        return None

    def _parentOverride(self):
        """Make sure this function is inherited."""
        return super(BaseWindow, self)

    def floating(self):
        """Return if the window is floating.
        As this is a base window only, it will always be floating.
        """
        return True

    def move(self, x, y):
        if self.dockable():
            return self._parentOverride().move(x, y)
        return super(BaseWindow, self).move(x, y)
    
    def geometry(self):
        if self.dockable():
            return self._parentOverride().geometry()
        return super(BaseWindow, self).geometry()

    def frameGeometry(self):
        if self.dockable():
            return self._parentOverride().frameGeometry()
        return super(BaseWindow, self).frameGeometry()

    def rect(self):
        if self.dockable():
            return self._parentOverride().rect()
        return super(BaseWindow, self).rect()

    def width(self):
        if self.dockable():
            return self._parentOverride().width()
        return super(BaseWindow, self).width()

    def height(self):
        if self.dockable():
            return self._parentOverride().height()
        return super(BaseWindow, self).height()

    def x(self):
        if self.dockable():
            return self._parentOverride().x()
        return super(BaseWindow, self).x()

    def y(self):
        if self.dockable():
            return self._parentOverride().y()
        return super(BaseWindow, self).y()

    def resize(self, width, height):
        if self.dockable():
            return self._parentOverride().resize(width, height)
        return super(BaseWindow, self).resize(width, height)

    def centreWindow(self, parentGeometry=None, childGeometry=None):
        """Centre the current window to its parent.
        In the case of overrides, the parent or child geometry may be provided.
        """
        if parentGeometry is None:
            try:
                parentGeometry = self.parent().frameGeometry()

            #If there is no parent, use the screen size
            except AttributeError:
                screenSize = QtWidgets.QApplication.desktop().screenGeometry()
                class _TempRect(object):
                    def __init__(self, x=0, y=0, width=0, height=0):
                        self.__x = x
                        self.__y = y
                        self.__width = width
                        self.__height = height
                    x = lambda self: self.__x
                    y = lambda self: self.__y
                    width = lambda self: self.__width
                    height = lambda self: self.__height
                parentGeometry = _TempRect(width=screenSize.width(), height=screenSize.height())

        if childGeometry is None:
            childGeometry = self.frameGeometry()

        self.move(
            parentGeometry.x() + (parentGeometry.width() - childGeometry.width()) / 2,
            parentGeometry.y() + (parentGeometry.height() - childGeometry.height()) / 2
        )

    def deferred(self, func, *args, **kwargs):
        """Placeholder for program specific deferred functions."""
        func()

    def exists(self):
        """Return if the window currently exists.
        For most cases the value will only ever be True.
        """
        return True
