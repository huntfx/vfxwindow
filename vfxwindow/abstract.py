"""Abstract class to inherit that contains the core functionality."""

from __future__ import absolute_import

import json
import os
import tempfile
import uuid
from collections import defaultdict
from contextlib import contextmanager
from functools import partial

from .palette import savePaletteData, setPalette
from .utils import hybridmethod, setCoordinatesToScreen
from .utils.Qt import QtCore, QtGui, QtWidgets


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


class AbstractWindow(QtWidgets.QMainWindow):
    """Base class for all Qt windows.

    Each window must be provided with a unique "WindowID" attribute to
    enable the saving and loading of its location betweem sessions.
    This will also enable the automatic closing of a previous window if
    a new one is launched, via the clearWindowInstance methods. A
    "WindowName" attribute will determine the window title, or it will
    default to "New Window" if not set.

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
    clearedInstance = QtCore.Signal()
    windowReady = QtCore.Signal()
    
    _WINDOW_INSTANCES = {}

    def __init__(self, parent=None, **kwargs):
        super(AbstractWindow, self).__init__(parent, **kwargs)
        
        # Setup window attributes and saving
        self.enableSaveWindowPosition(True)
        self.__forceDisableSaving = not hasattr(self, 'WindowID')
        if self.__forceDisableSaving:
            self.WindowID = uuid.uuid4()
        self.setWindowTitle(getattr(self, 'WindowName', 'New Window'))

        # Track settings that to be read by any inherited windows
        self.batch = False
        self.maya = False
        self.nuke = False
        self.houdini = False
        self.fusion = False
        self.blender = False
        self.unreal = False
        self.standalone = False

        # Read settings
        self._windowDataPath = getWindowSettingsPath(self.WindowID)
        tempFolder = os.path.dirname(self._windowDataPath)
        if not os.path.exists(tempFolder):
            os.makedirs(tempFolder)
        self.windowSettings = getWindowSettings(self.WindowID, path=self._windowDataPath)

        self._signals = defaultdict(list)
        self.__closed = False
        self.__dockable = getattr(self, 'WindowDockable', False)
        self.__wasDocked = None
        self.__initialPosOverride = None

        # Store the window data so it can be closed later
        # In some cases such as Maya's layoutDialog, the window will
        # be deleted too early, so we can't use weakref.proxy(self)
        AbstractWindow._WINDOW_INSTANCES[self.WindowID] = {
            'window': self,
            'callback': {}
        }

    def processEvents(self):
        """Wrapper over the inbult processEvents method.
        This forces the GUI to update in the middle of calculations.
        """
        QtWidgets.QApplication.processEvents()

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
                signals.append((signal, func))
        return signals

    def signalConnect(self, signal, func, group=None):
        """Add a new signal for the current group.

        >>> self.signalConnect(widget.currentIndexChanged, self.widgetChanged, 'widget_changed')
        """
        self._signals[group].append((signal, func))
        signal.connect(func)
        return func

    @contextmanager
    def signalPause(self, *groups):
        """Pause a certain set of signals during execution.
        This will remove the signals, and re-apply them after.
        """
        if not groups:
            groups = self._signals
        
        signalCache = {}
        for group in groups:
            signalCache[group] = self.signalDisconnect(group)

        yield

        for group in groups:
            for signal, func in signalCache[group]:
                self.signalConnect(signal, func, group=group)

    def dockable(self, raw=False):
        """Return if the window is dockable.
        
        Parameters:
            raw (bool): If True, get the current state of the window,
                otherwise get the current setting, which may require
                a reload to apply if it's been changed.
        """
        if not raw and self.__wasDocked is not None:
            return self.__wasDocked
        return self.__dockable

    def setDockable(self, dockable, override=False):
        """Set if the window should be dockable.

        Parameters:
            override (bool): If the dockable raw value should be set.
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
        return saveWindowSettings(self.WindowID, self.windowSettings, path=path)

    def setWindowIcon(self, icon):
        """Convert a string to a QIcon if needed."""
        if not isinstance(icon, QtGui.QIcon):
            icon = QtGui.QIcon(icon)
        super(AbstractWindow, self).setWindowIcon(icon)

    def displayMessage(self, title, message, details=None, buttons=('Ok',), defaultButton=None, cancelButton=None, checkBox=None):
        """Display a popup box.

        The setCheckBox command was added in Qt 5.2.
        Even if it is not available, its state will still be returned.
        
        Parameters:
            title (str): Title of the window.
            message (str): Short sentence with a question or statement.
            details (str): Add extra information if required.
            buttons (list of str): Define which buttons to use, must be a QMessageBox StandardButton.
                It is required as a string for compatibility with other programs.
            defaultButton (str): Define which button is selected by default.
            cancelButton (str): Define which button acts as the no/cancel option.
            checkBox (QtWidgets.QCheckBox): Add a checkbox (Qt 5.2+ only).

        Returns:
            if checkBox:
                (buttonClicked (str), checked (bool))
            else:
                buttonClicked (str)
        """
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        if details is not None:
            msg.setInformativeText(details)

        # Store a list of buttons so we can figure out what was pressed
        buttonDict = {}
        for button in buttons:
            buttonDict[getattr(QtWidgets.QMessageBox, button)] = button

        # Set the buttons
        standardButtons = 0
        for button in buttonDict:
            standardButtons |= button
        msg.setStandardButtons(standardButtons)
        if defaultButton is None:
            msg.setDefaultButton(getattr(QtWidgets.QMessageBox, buttons[-1]))
        else:
            msg.setDefaultButton(getattr(QtWidgets.QMessageBox, defaultButton))
        if cancelButton is not None:
            msg.setEscapeButton(getattr(QtWidgets.QMessageBox, cancelButton))

        if checkBox is not None:
            if not isinstance(checkBox, QtWidgets.QCheckBox):
                checkBox = QtWidgets.QCheckBox(checkBox)
            try:
                msg.setCheckBox(checkBox)
            except AttributeError:
                pass

        # Get the string of the button that was clicked
        result = buttonDict[msg.exec_()]

        if checkBox is not None:
            return (result, checkBox.isChecked())
        return result

    @hybridmethod
    def show(cls, self, *args, **kwargs):
        """Show the window and load its position."""
        # The window has already been initialised
        if self is not cls:
            return super(AbstractWindow, self).show()
        
        # Close down any existing windows and open a new one
        try:
            cls.clearWindowInstance(cls.WindowID)
        except AttributeError:
            pass
        new = cls(*args, **kwargs)
        super(AbstractWindow, new).show()
        new.loadWindowPosition()
        new.deferred(new.windowReady.emit)
        return new

    @classmethod
    def instance(cls, parent=None, **kwargs):
        """Setup the window without showing it.
        Used for parenting to other windows.

        Note: If not using a parent of AbstractWindow, then
        cls.clearWindowInstance(cls.WindowID) will need to be manually
        run to unregister callbacks.

        Example:
            layout.addWidget(OtherWindow.instance(self).centralWidget())
            # The above line will link the close callbacks and things
        """
        # Store the ID of an existing window
        tempID = None
        if cls.WindowID in cls._WINDOW_INSTANCES:
            tempID = uuid.uuid4().hex
            cls._WINDOW_INSTANCES[tempID] = cls._WINDOW_INSTANCES.pop(cls.WindowID)

        # Create window with new ID and disable saving
        new = cls(parent=parent, **kwargs)
        new.WindowID = uuid.uuid4().hex
        cls._WINDOW_INSTANCES[new.WindowID] = cls._WINDOW_INSTANCES.pop(cls.WindowID)
        new.enableSaveWindowPosition(False)

        # Return old ID
        if tempID is not None:
            cls._WINDOW_INSTANCES[cls.WindowID] = cls._WINDOW_INSTANCES.pop(tempID)

        # Connect/emit the signals
        new.deferred(new.windowReady.emit)
        if isinstance(parent, AbstractWindow):
            parent.clearedInstance.connect(partial(cls.clearWindowInstance, new.WindowID))
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
            windowID = self.WindowID

        if windowID in cls._WINDOW_INSTANCES:
            if delete and self is cls:
                return cls.clearWindowInstance(windowID)
            return cls._WINDOW_INSTANCES[windowID]

    @classmethod
    def clearWindowInstance(cls, windowID):
        """Close the last class instance.
        This must be subclassed if the window needs to be closed.

        A signal will be emitted as it will be attached to any child windows too.
        In the case of a dialog, it will be deleted by now, so ignore.
        """
        inst = cls._WINDOW_INSTANCES.pop(windowID, None)
        if inst is not None and not getattr(inst['window'], 'ForceDialog', False):
            try:
                inst['window'].clearedInstance.emit()
            except RuntimeError:
                pass
        return inst

    @classmethod
    def clearWindowInstances(cls):
        """Close down every loaded window."""
        for windowID in tuple(cls._WINDOW_INSTANCES):
            cls.clearWindowInstance(windowID)

    def close(self):
        """Close the window and mark it as closed."""
        self.__closed = True
        super(AbstractWindow, self).close()

    def isClosed(self):
        """Return if the window has been closed."""
        return self.__closed

    def saveWindowPalette(self, program, version):
        """Save the palette as a file.
        This is mainly to be used if the window palette is auto generated.
        """
        return savePaletteData(program, version, self.palette())
    
    def setWindowPalette(self, program, version=None, style=True, **kwargs):
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
        return super(AbstractWindow, self)

    def floating(self):
        """Return if the window is floating.
        As this is a base window only, it will always be floating.
        """
        return True

    def move(self, x, y=None):
        if isinstance(x, QtCore.QPoint):
            y = x.y()
            x = x.x()
        if self.dockable():
            return self._parentOverride().move(x, y)
        return super(AbstractWindow, self).move(x, y)
    
    def geometry(self):
        if self.dockable():
            return self._parentOverride().geometry()
        return super(AbstractWindow, self).geometry()

    def frameGeometry(self):
        if self.dockable():
            return self._parentOverride().frameGeometry()
        return super(AbstractWindow, self).frameGeometry()

    def rect(self):
        if self.dockable():
            return self._parentOverride().rect()
        return super(AbstractWindow, self).rect()

    def width(self):
        if self.dockable():
            return self._parentOverride().width()
        return super(AbstractWindow, self).width()

    def height(self):
        if self.dockable():
            return self._parentOverride().height()
        return super(AbstractWindow, self).height()

    def x(self):
        if self.dockable():
            return self._parentOverride().x()
        return super(AbstractWindow, self).x()

    def y(self):
        if self.dockable():
            return self._parentOverride().y()
        return super(AbstractWindow, self).y()

    def resize(self, width, height=None):
        if isinstance(width, QtCore.QSize):
            height = width.height()
            width = width.width()
        if self.dockable():
            return self._parentOverride().resize(width, height)
        return super(AbstractWindow, self).resize(width, height)

    def centreWindow(self, parentGeometry=None, childGeometry=None):
        """Centre the current window to its parent.
        In the case of overrides, the parent or child geometry may be provided.
        """
        if parentGeometry is None:
            try:
                parentGeometry = self.parent().frameGeometry()
            except AttributeError:
                parentGeometry = QtWidgets.QApplication.desktop().screenGeometry()

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

    @hybridmethod
    def removeCallbacks(cls, self, *args, **kwargs):
        pass
