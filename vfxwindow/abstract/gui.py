"""Abstract class to inherit that contains the core functionality."""

from __future__ import absolute_import, division

import inspect
import os
import sys
import uuid
from collections import defaultdict
from contextlib import contextmanager
from functools import partial
from Qt import QtCore, QtGui, QtWidgets

from .application import AbstractApplication
from .callbacks import AbstractCallbacks
from ..utils import hybridmethod, setCoordinatesToScreen, saveWindowSettings, getWindowSettings, getWindowSettingsPath
from ..utils.palette import savePaletteData, setPalette


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

    CallbackClass = None

    _WINDOW_INSTANCES = {}

    def __init__(self, parent=None, **kwargs):
        super(AbstractWindow, self).__init__(parent, **kwargs)

        callbackClass = type(self).CallbackClass
        if callbackClass is not None:
            self.callbacks = callbackClass(self)
        else:
            self.callbacks = AbstractCallbacks(self)

        # Setup window attributes and saving
        self.enableSaveWindowPosition(True)
        self.__forceDisableSaving = not hasattr(self, 'WindowID')
        if self.__forceDisableSaving:
            self.WindowID = uuid.uuid4()
        self.setWindowTitle(getattr(self, 'WindowName', 'New Window'))
        self._setChildWindow(False)

        # Read settings
        self._windowDataPath = getWindowSettingsPath(self.WindowID)
        tempFolder = os.path.dirname(self._windowDataPath)
        if not os.path.exists(tempFolder):
            os.makedirs(tempFolder)
        self.windowSettings = getWindowSettings(self.WindowID, path=self._windowDataPath)

        self._signals = defaultdict(list)
        self._windowClosed = self._windowLoaded = False
        self.__dockable = getattr(self, 'WindowDockable', False)
        self.__wasDocked = None
        self.__initialPosOverride = None
        self.__signalCache = defaultdict(list)

        # Store the window data so it can be closed later
        # In some cases such as Maya's layoutDialog, the window will
        # be deleted too early, so we can't use weakref.proxy(self)
        AbstractWindow._WINDOW_INSTANCES[self.WindowID] = {
            'window': self,
            'callback': {}
        }

        self.windowReady.connect(lambda: setattr(self, '_windowLoaded', True))
        self.windowReady.connect(self.raise_)

    @property
    def application(self):
        """Get the current application.

        Raises:
            NotImplementedError: If not set for the current application.

        Returns:
            Application class instance (treat it as a string) or None.
        """
        raise NotImplementedError('`{}.application` not implemented.'.format(type(self).__name__))

    @property
    def batch(self):
        """Determine if the application is in batch mode.
        Deprecated and will be removed in 2.0.
        """
        if self.application is None:
            return False
        return self.application.batch

    @property
    def maya(self):
        """Determine if the application is Maya.
        Deprecated and will be removed in 2.0.
        """
        return self.application == 'Maya'

    @property
    def nuke(self):
        """Determine if the application is Nuke.
        Deprecated and will be removed in 2.0.
        """
        return self.application == 'Nuke'

    @property
    def houdini(self):
        """Determine if the application is Houdini.
        Deprecated and will be removed in 2.0.
        """
        return self.application == 'Houdini'

    @property
    def max(self):
        """Determine if the application is 3ds Max.
        Deprecated and will be removed in 2.0.
        """
        return self.application == '3ds Max'

    @property
    def fusion(self):
        """Determine if the application is Blackmagic Fusion.
        Deprecated and will be removed in 2.0.
        """
        return self.application == 'Fusion'

    @property
    def blender(self):
        """Determine if the application is Blender.
        Deprecated and will be removed in 2.0.
        """
        return self.application == 'Blender'

    @property
    def unreal(self):
        """Determine if the application is Unreal Engine.
        Deprecated and will be removed in 2.0.
        """
        return self.application == 'Unreal Engine'

    @property
    def substancePainter(self):
        """Determine if the application is Substance Painter.
        Deprecated and will be removed in 2.0.
        """
        return self.application == 'Substance Painter'

    @property
    def substanceDesigner(self):
        """Determine if the application is Substance Designer.
        Deprecated and will be removed in 2.0.
        """
        return self.application == 'Substance Designer'

    @property
    def cryengine(self):
        """Determine if the application is CryEngine Sandbox.
        Deprecated and will be removed in 2.0.
        """
        return self.application == 'CryEngine Sandbox'

    @property
    def standalone(self):
        """Determine if the window is a standalone window.
        Deprecated and will be removed in 2.0.
        """
        return self.application is None

    def signalConnect(self, signal, func, type=QtCore.Qt.AutoConnection, group=None):
        """Add a new signal for the current group.

        Example:
            >>> self.signalConnect(widget.currentIndexChanged, self.widgetChanged, group='widget_changed')
        """
        if self.signalPaused(group):
            self.__signalCache[group].append((signal, func, type))
        else:
            self._signals[group].append((signal, func, type))
            signal.connect(func)
        return func

    def signalDisconnect(self, group, _pause=False):
        """Disconnect and return all functions for a current group.
        If none exist, and empty list will be returned.

        Example:
            >>> self.signalDisconnect('widget_changed')
            [self.widgetChanged]
            >>> self.signalDisconnect('widget_changed')
            []
        """
        signals = []

        # If paused, then just remove the signals from cache
        if not _pause and self.signalPaused(group):
            signals += self.__signalCache.pop(group)

        # Disconnect the signals
        for (signal, func, type) in self._signals.pop(group, ()):
            try:
                signal.disconnect(func)
            except RuntimeError:
                pass
            else:
                signals.append((signal, func, type))
        return signals

    @contextmanager
    def signalPause(self, *groups):
        """Pause a certain set of signals during execution.
        This will remove the signals, and re-apply them after.
        """
        skip = set()
        if not groups:
            groups = self._signals
        groups = set(groups)

        for group in groups:
            if self.signalPaused(group):
                skip.add(group)
            self.__signalCache[group] += self.signalDisconnect(group, _pause=True)

        try:
            yield

        finally:
            for group in set(groups) - skip:
                if group in self.__signalCache:
                    for signal, func, type in self.__signalCache.pop(group):
                        self.signalConnect(signal, func, type, group=group)

    def signalPaused(self, group):
        """Determine if a signal group is paused."""
        return group in self.__signalCache

    def _getSettingsKey(self):
        """Get the key to use when saving settings."""
        if self.application is not None and self.application.batch:
            return 'batch'
        if self.dockable():
            return 'dock'
        elif self.isDialog():
            return 'dialog'
        elif self.isInstance():
            return 'instance'
        else:
            return 'main'

    def dockable(self, raw=False):
        """Return if the window is dockable.

        Parameters:
            raw (bool): If True, get the current state of the window,
                otherwise get the current setting, which may require
                a reload to apply if it's been changed.
        """
        if raw:
            return self.__dockable
        if self.isInstance():
            return False
        if self.__wasDocked is not None:
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
        return not self.floating()

    def setDocked(self, docked):
        """Force the window to dock or undock."""
        pass

    def setFloating(self, floating):
        """Force the window to dock or undock."""
        self.setDocked(not floating)

    def isDialog(self):
        """Return if the window is a dialog.
        Note that this will not work in __init__().
        If it is needed, attach it to the windowReady signal instead.
        """
        try:
            return isinstance(self.parent(), QtWidgets.QDialog)
        except RuntimeError:
            return False

    def loadWindowPosition(self):
        """Load the previous position or centre the window.
        The loading must be done in an override.
        """
        if self.isInstance():
            return

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
        if self.isInstance():
            return

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

    def about(self, text=None):
        """Make an "about" popup message.
        If no text is provided, this will first attempt to read the
        docstring of the module, and if that fails, it will grab
        the docstring of the current class.
        """
        if text is None or isinstance(text, bool):
            docstring = inspect.getmodule(self).__doc__ or self.__class__.__doc__
            if docstring is None:
                raise ValueError('unable to find docstring')
            text = inspect.cleandoc(docstring)

        try:
            self.displayMessage(
                title='About {}'.format(self.WindowName),
                message=text,
            )
        except AttributeError:
            self.displayMessage(
                title='About',
                message=text,
            )

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
    def dialog(cls, parent=None, *args, **kwargs):
        """Create the window as a dialog.
        Methods of .dialogAccept and .dialogReject will be added.
        Any variables given to these will be returned.

        Output: (accepted[bool], data[list])
        """
        # Create application if it doesn't exist
        inst = app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication(sys.argv)

        dialog = QtWidgets.QDialog(parent=parent)
        dialog.setWindowTitle(getattr(cls, 'WindowName', 'New Window'))
        if inst is None:
            app.setActiveWindow(dialog)

        # Inheirt the class to set attributes
        class windowClass(cls):
            WindowDockable = False
            _DialogData = []

            # Method of getting data returned from dialog
            def dialogAccept(self, *args):
                self._DialogData += args
                return dialog.accept()

            def dialogReject(self, *args):
                self._DialogData += args
                return dialog.reject()

        # Setup layout
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        #layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        windowInstance = windowClass(*args, **kwargs)
        layout.addWidget(windowInstance)
        dialog.setLayout(layout)

        # Finish setting up window
        windowInstance.loadWindowPosition()
        windowInstance.windowReady.emit()

        try:
            return (dialog.exec_(), windowInstance._DialogData)
        finally:
            windowInstance.saveWindowPosition()
            windowClass.clearWindowInstance(windowClass.WindowID)

    def setVisible(self, visible):
        """Override setVisible to make sure it behaves like show/hide.
        This can cause recursion errors, so make sure the window has
        been loaded and not closed.
        """
        if not self.isLoaded() or self.isInstance() or self.isDialog():
            return super(AbstractWindow, self).setVisible(visible)
        if visible:
            return self.show()
        return self.hide()

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
        new._setChildWindow(True)
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

    def isInstance(self):
        """Get if the window is a child of another window."""
        return self.__childWindow

    def _setChildWindow(self, value):
        """Mark if the window is a child of another window.
        This should not be manually called.
        """
        self.__childWindow = value

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
        if inst is not None and not inst['window'].isDialog():
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

    def closeEvent(self, event):
        """Close the window and mark it as closed."""
        self._windowClosed = True
        self.clearWindowInstance(self.WindowID)
        if self.isDialog():
            return self.parent().close()
        return super(AbstractWindow, self).closeEvent(event)

    def isClosed(self):
        """Return if the window has been closed."""
        return self._windowClosed

    def isLoaded(self):
        """Return if the window is currently loaded."""
        return self._windowLoaded and not self.isClosed()

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
        return not self.isInstance()

    def move(self, x, y=None):
        if self.isInstance():
            return
        if isinstance(x, QtCore.QPoint):
            y = x.y()
            x = x.x()
        if self.dockable():
            return self._parentOverride().move(x, y)
        elif self.isDialog():
            return self.parent().move(x, y)
        return super(AbstractWindow, self).move(x, y)

    def geometry(self):
        if not self.isInstance():
            if self.dockable():
                return self._parentOverride().geometry()
            elif self.isDialog():
                return self.parent().geometry()
        return super(AbstractWindow, self).geometry()

    def frameGeometry(self):
        if not self.isInstance():
            if self.dockable():
                return self._parentOverride().frameGeometry()
            elif self.isDialog():
                return self.parent().frameGeometry()
        return super(AbstractWindow, self).frameGeometry()

    def rect(self):
        if not self.isInstance():
            if self.dockable():
                return self._parentOverride().rect()
            elif self.isDialog():
                return self.parent().rect()
        return super(AbstractWindow, self).rect()

    def width(self):
        if not self.isInstance():
            if self.dockable():
                return self._parentOverride().width()
            elif self.isDialog():
                return self.parent().width()
        return super(AbstractWindow, self).width()

    def height(self):
        if not self.isInstance():
            if self.dockable():
                return self._parentOverride().height()
            elif self.isDialog():
                return self.parent().height()
        return super(AbstractWindow, self).height()

    def x(self):
        if not self.isInstance():
            if self.dockable():
                return self._parentOverride().x()
            elif self.isDialog():
                return self.parent().x()
        return super(AbstractWindow, self).x()

    def y(self):
        if not self.isInstance():
            if self.dockable():
                return self._parentOverride().y()
            elif self.isDialog():
                return self.parent().y()
        return super(AbstractWindow, self).y()

    def resize(self, width, height=None):
        if self.isInstance():
            return

        if isinstance(width, QtCore.QSize):
            height = width.height()
            width = width.width()
        if self.dockable():
            return self._parentOverride().resize(width, height)
        elif self.isDialog():
            return self.parent().resize(width, height)
        return super(AbstractWindow, self).resize(width, height)

    def setMinimumWidth(self, *args, **kwargs):
        if self.isDialog():
            return self.parent().setMinimumWidth(*args, **kwargs)
        return super(AbstractWindow, self).setMinimumWidth(*args, **kwargs)

    def setFixedWidth(self, *args, **kwargs):
        if self.isDialog():
            return self.parent().setFixedWidth(*args, **kwargs)
        return super(AbstractWindow, self).setFixedWidth(*args, **kwargs)

    def setMaximumWidth(self, *args, **kwargs):
        if self.isDialog():
            return self.parent().setMaximumWidth(*args, **kwargs)
        return super(AbstractWindow, self).setMaximumWidth(*args, **kwargs)

    def setMinimumHeight(self, *args, **kwargs):
        if self.isDialog():
            return self.parent().setMinimumHeight(*args, **kwargs)
        return super(AbstractWindow, self).setMinimumHeight(*args, **kwargs)

    def setFixedHeight(self, *args, **kwargs):
        if self.isDialog():
            return self.parent().setFixedHeight(*args, **kwargs)
        return super(AbstractWindow, self).setFixedHeight(*args, **kwargs)

    def setMaximumHeight(self, *args, **kwargs):
        if self.isDialog():
            return self.parent().setMaximumHeight(*args, **kwargs)
        return super(AbstractWindow, self).setMaximumHeight(*args, **kwargs)

    def setMinimumSize(self, *args, **kwargs):
        if self.isDialog():
            return self.parent().setMinimumSize(*args, **kwargs)
        return super(AbstractWindow, self).setMinimumSize(*args, **kwargs)

    def setFixedSize(self, *args, **kwargs):
        if self.isDialog():
            return self.parent().setFixedSize(*args, **kwargs)
        return super(AbstractWindow, self).setFixedSize(*args, **kwargs)

    def setMaximumSize(self, *args, **kwargs):
        if self.isDialog():
            return self.parent().setMaximumSize(*args, **kwargs)
        return super(AbstractWindow, self).setMaximumSize(*args, **kwargs)

    def centreWindow(self, parentGeometry=None, childGeometry=None):
        """Centre the current window to its parent.
        In the case of overrides, the parent or child geometry may be provided.
        """
        if parentGeometry is None or childGeometry is None:
            if self.isDialog():
                base = self.parent()
            else:
                base = self

            if parentGeometry is None:
                try:
                    parentGeometry = base.parent().frameGeometry()

                except AttributeError:
                    # PySide2 / PySide6
                    try:
                        parentGeometry = QtWidgets.QApplication.primaryScreen().geometry()

                    # PySide / PySide2 (deprecated)
                    except AttributeError:
                        parentGeometry = QtWidgets.QApplication.desktop().screenGeometry()

            if childGeometry is None:
                childGeometry = base.frameGeometry()

        self.move(
            parentGeometry.x() + (parentGeometry.width() - childGeometry.width()) // 2,
            parentGeometry.y() + (parentGeometry.height() - childGeometry.height()) // 2
        )

    def deferred(self, func, *args, **kwargs):
        """Placeholder for program specific deferred functions."""
        func(*args, **kwargs)

    def exists(self):
        """Return if the window currently exists.
        For most cases the value will only ever be True.
        """
        return True
