"""Window class for Nuke.

TODO: Get callbacks from https://learn.foundry.com/nuke/developers/110/pythonreference/
TODO: Figure out how to launch a floating panel
"""

from __future__ import absolute_import, print_function

import uuid
from collections import defaultdict
from functools import partial
from Qt import QtWidgets

import nuke
from nukescripts import panels, utils

from .application import Application
from .callbacks import NukeCallbacks
from ..abstract.gui import AbstractWindow
from ..standalone.gui import StandaloneWindow
from ..utils import hybridmethod, setCoordinatesToScreen, searchGlobals, getWindowSettings


class RuntimeDraggingError(RuntimeError):
    """Custom error message for when a window is being dragged."""

    def __init__(self):
        super(RuntimeDraggingError, self).__init__("window is currently in a quantum state (while dragging it technically doesn't exist)")


def getMainWindow():
    """Returns the Nuke main window.
    If nothing can be found, None will be returned.
    Source: https://github.com/fredrikaverpil/pyvfx-boilerplate/blob/master/boilerplate.py
    """
    for obj in QtWidgets.QApplication.topLevelWidgets():
        if isinstance(obj, QtWidgets.QMainWindow) and obj.metaObject().className() == 'Foundry::UI::DockMainWindow':
            return obj


def deleteQtWindow(windowId):
    """Delete a window.
    Source: https://github.com/fredrikaverpil/pyvfx-boilerplate/blob/master/boilerplate.py
    """
    for obj in QtWidgets.QApplication.allWidgets():
        if obj.objectName() == windowId:
            obj.deleteLater()


def _removeMargins(widget):
    """Remove Nuke margins when docked UI
    Source: https://gist.github.com/maty974/4739917
    """
    for parent in (widget.parentWidget().parentWidget(), widget.parentWidget().parentWidget().parentWidget().parentWidget()):
        parent.layout().setContentsMargins(0, 0, 0, 0)


def _checkContextSupported():
    """Determine if the current context is supported."""
    if Application.loaded and not QtWidgets.QApplication.topLevelWidgets():
        raise NotImplementedApplicationError('Nuke GUI not supported in terminal mode, launch nuke with the --tg flag instead.')


class Pane(object):
    @classmethod
    def get(cls, value=None):
        if value is not None:
            return nuke.getPaneFor(value)
        return cls.auto()

    @classmethod
    def auto(cls):
        """Automatically select a pane to attach to.
        If there are somehow no panels that exist then None will be returned.
        """
        for pane_func in cls.__PRIORITY:
            pane = pane_func.__get__(cls, None)()
            if pane is not None:
                return pane

    @classmethod
    def find(cls, windowID):
        """Find which pane the WindowID is docked to."""
        current_pane = nuke.getPaneFor(windowID)
        if current_pane is None:
            return None
        for pane_func in cls.__PRIORITY:
            index = 1
            while True:
                pane = pane_func.__get__(cls, None)(index)
                if pane is None:
                    break
                if pane == current_pane:
                    return pane_func.__get__(cls, None)(index, name=True)
                index += 1

    @classmethod
    def Properties(cls, index=1, name=False):
        panel_name = 'Properties.{}'.format(index)
        if name:
            return panel_name
        return nuke.getPaneFor(panel_name)

    @classmethod
    def NodeGraph(cls, index=1, name=False):
        panel_name = 'DAG.{}'.format(index)
        if name:
            return panel_name
        return nuke.getPaneFor(panel_name)

    @classmethod
    def Viewer(cls, index=1, name=False):
        panel_name = 'Viewer.{}'.format(index)
        if name:
            return panel_name
        return nuke.getPaneFor(panel_name)

    @classmethod
    def Progress(cls, index=1, name=False):
        panel_name = 'Progress.{}'.format(index)
        if name:
            return panel_name
        return nuke.getPaneFor(panel_name)

    @classmethod
    def DopeSheet(cls, index=1, name=False):
        panel_name = 'DopeSheet.{}'.format(index)
        if name:
            return panel_name
        return nuke.getPaneFor(panel_name)

    @classmethod
    def Toolbar(cls, index=1, name=False):
        panel_name = 'Toolbar.{}'.format(index)
        if name:
            return panel_name
        return nuke.getPaneFor(panel_name)

    @classmethod
    def CurveEditor(cls, index=1, name=False):
        panel_name = 'Curve Editor.{}'.format(index)
        if name:
            return panel_name
        return nuke.getPaneFor(panel_name)

    @classmethod
    def PixelAnalyzer(cls, index=1, name=False):
        panel_name = 'Pixel Analyzer.{}'.format(index)
        if name:
            return panel_name
        return nuke.getPaneFor(panel_name)

    @classmethod
    def ErrorConsole(cls, index=1, name=False):
        panel_name = 'Error Console.{}'.format(index)
        if name:
            return panel_name
        return nuke.getPaneFor(panel_name)

    @classmethod
    def ScriptEditor(cls, index=1, name=False):
        panel_name = 'uk.co.thefoundry.scripteditor.{}'.format(index)
        if name:
            return panel_name
        return nuke.getPaneFor(panel_name)

    @classmethod
    def Histogram(cls, index=1, name=False):
        panel_name = 'uk.co.thefoundry.histogram.{}'.format(index)
        if name:
            return panel_name
        return nuke.getPaneFor(panel_name)

    @classmethod
    def Waveform(cls, index=1, name=False):
        panel_name = 'uk.co.thefoundry.waveformscope.{}'.format(index)
        if name:
            return panel_name
        return nuke.getPaneFor(panel_name)

    @classmethod
    def Vectorscope(cls, index=1, name=False):
        panel_name = 'uk.co.thefoundry.vectorscope.{}'.format(index)
        if name:
            return panel_name
        return nuke.getPaneFor(panel_name)

    __PRIORITY = [
        Properties,
        NodeGraph,
        Viewer,
        DopeSheet,
        CurveEditor,
        PixelAnalyzer,
        Progress,
        ErrorConsole,
        ScriptEditor,
        Histogram,
        Waveform,
        Vectorscope,
        Toolbar,
    ]


class NukeCommon(object):

    CallbackClass = NukeCallbacks

    @property
    def application(self):
        """Get the current application."""
        return Application


class NukeWindow(NukeCommon, AbstractWindow):
    """Base class for docking windows in Nuke.

    Docked Window Workarounds:
        Because Nuke only "hides" docked windows and never closes them,
        a few special workarounds need to be done on some features.

        Window Position:
            This must be run every time the window is hidden, to ensure
            the location is as up to date as possible. The process of
            dragging a window actually sends a hideEvent, but will
            cause errors when trying to query positions as it gets
            detached from all parents.

        Callbacks:
            Since there is no closeEvent to catch, every callback will
            unregister when the window is hidden, and be registered
            again when the window appears again.
            By defining a "checkForChanges" method, code can be run
            after re-registering the callbacks.
    """

    _CALLBACKS = {
        'onUserCreate': ('addOnUserCreate', 'removeOnUserCreate'),
        'onCreate': ('addOnCreate', 'removeOnCreate'),
        'onScriptLoad': ('addOnScriptLoad', 'removeOnScriptLoad'),
        'onScriptSave': ('addOnScriptSave', 'removeOnScriptSave'),
        'onScriptClose': ('addOnScriptClose', 'removeOnScriptClose'),
        'onDestroy': ('addOnDestroy', 'removeOnDestroy'),
        'knobChanged': ('addKnobChanged', 'removeKnobChanged'),
        'updateUI': ('addUpdateUI', 'removeUpdateUI'),
    }

    def __init__(self, parent=None, dockable=True, **kwargs):
        """Create the Nuke window.
        By default dockable must be True as Nuke provides no control
        over it when creating a panel.
        """
        _checkContextSupported()

        if parent is None:
            parent = getMainWindow()
        super(NukeWindow, self).__init__(parent, **kwargs)

        self._isHiddenNk = False
        self.setDockable(dockable, override=True)

        # Fix for parent bug
        # See NukeWindow.parent for more information
        self.__useNukeTemporaryParent = True
        self.windowReady.connect(partial(setattr, self, '__useNukeTemporaryParent', False))

        # This line seemed to be recommended, but I'm not sure why
        #if not self.dockable():
        #    self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

    def closeEvent(self, event):
        """Special case for closing docked windows."""
        super(NukeWindow, self).clearWindowInstance(self.WindowID)

        if self.dockable():
            if self.exists():
                try:
                    #Delete the pane if it is floating by itself
                    if self.floating(alternative=True) and self.siblings() == 1:
                        self.parent().parent().parent().parent().parent().parent().parent().parent().parent().close()

                    #Remove the tab and pane if by itself
                    else:
                        self.parent().parent().parent().parent().parent().parent().parent().close()
                        deleteQtWindow(self.WindowID)

                except RuntimeDraggingError:
                    pass
        else:
            self.saveWindowPosition()
        return super(NukeWindow, self).closeEvent(event)

    def setDefaultSize(self, width, height):
        """Override of setDefaultSize to disable it if window is docked."""
        if not self.dockable():
            super(NukeWindow, self).setDefaultSize(width, height)

    def setDefaultWidth(self, width):
        """Override of setDefaultWidth to disable it if window is docked."""
        if not self.dockable():
            super(NukeWindow, self).setDefaultWidth(width)

    def setDefaultHeight(self, height):
        """Override of setDefaultHeight to disable it if window is docked."""
        if not self.dockable():
            super(NukeWindow, self).setDefaultHeight(height)

    def setDefaultPosition(self, x, y):
        """Override of setDefaultPosition to disable it if window is docked."""
        if not self.dockable():
            super(NukeWindow, self).setDefaultPosition(x, y)

    def setWindowPalette(self, program, version=None, style=True, force=False):
        """Set the palette of the window.
        This will change the entire Nuke GUI so it's disabled by default.
        The force parameter can be set to override this behaviour.
        """
        if force:
            super(NukeWindow, self).setWindowPalette(program, version, style)

    def windowPalette(self):
        """Get the current window palette."""
        currentPalette = super(NukeWindow, self).windowPalette()
        if currentPalette is None:
            return 'Nuke.{}'.format(int(self.application.version))
        return currentPalette

    def exists(self, alternative=False):
        """Check if the window still exists.
        See if it is attached to any pane, or check the parents up to the QStackedWidget.
        """
        if self.dockable():
            if alternative:
                return self.parent().parent().parent().parent().parent().parent().parent().parent() is not None
            return Pane.get(self.WindowID) is not None
        return not self.isClosed()

    def floating(self, alternative=False):
        """Determine if the window is floating."""
        if self.dockable():
            if alternative:
                try:
                    return self.parent().parent().parent().parent().parent().parent().parent().parent().parent().parent().parent().parent() is not None
                except AttributeError:
                    raise RuntimeDraggingError
            return Pane.find(self.WindowID) is None
        return True

    def siblings(self):
        """Count the number of siblings in the QStackedWidget."""
        if self.dockable():
            try:
                return self.parent().parent().parent().parent().parent().parent().parent().parent().count()
            except AttributeError:
                return 0
        return None

    def resize(self, *args, **kwargs):
        """Resize the window.
        Only resize after loading has finished if it's not docked to a panel.
        """
        if not self._windowLoaded:
            return self.windowReady.connect(partial(self.resize, *args, **kwargs))

        try:
            floating = self.floating()
        except RuntimeDraggingError:
            floating = False
        if not self.dockable() or floating:
            super(NukeWindow, self).resize(*args, **kwargs)

    def move(self, *args, **kwargs):
        """Move the window.
        Only move after loading has finished if it's not docked to a panel.
        """
        if not self._windowLoaded:
            return self.windowReady.connect(partial(self.move, *args, **kwargs))

        if not self.dockable() or self.floating():
            super(NukeWindow, self).move(*args, **kwargs)

    def getAttachedPane(self):
        """Find the name of the pane the window is attached to."""
        return Pane.find(self.WindowID)

    def saveWindowPosition(self):
        """Save the window location."""
        if self.application not in self.windowSettings:
            self.windowSettings[self.application] = {}
        settings = self.windowSettings[self.application]
        settings['docked'] = self.dockable(raw=True)

        key = self._getSettingsKey()
        if key not in settings:
            settings[key] = {}

        try:
            settings[key]['width'] = self.width()
            settings[key]['height'] = self.height()
            settings[key]['x'] = self.x()
            settings[key]['y'] = self.y()

            # Save docked specific settings
            if self.dockable():
                panel = self.getAttachedPane()
                if panel is not None:
                    settings[key]['panel'] = panel

        # Catch error if window is being dragged at this moment
        except RuntimeDraggingError as e:
            if not self.dockable():
                raise

        super(NukeWindow, self).saveWindowPosition()

    def loadWindowPosition(self):
        """Set the position of the window when loaded."""
        if self.dockable():
            return
        try:
            settings = self.windowSettings[self.application]['main']
            x = settings['x']
            y = settings['y']
            width = settings['width']
            height = settings['height']
        except KeyError:
            super(NukeWindow, self).loadWindowPosition()
        else:
            x, y = setCoordinatesToScreen(x, y, width, height, padding=5)
            self.resize(width, height)
            self.move(x, y)

    def _parentOverride(self, usePane=False):
        """Get the widget that contains the correct size and position on screen."""
        try:
            if usePane:
                pane = Pane.get(self.WindowID)
                if pane is None:
                    raise AttributeError()
                return pane
            if not self.floating(alternative=True):
                return self.parent().parent().parent().parent().parent().parent().parent().parent().parent()
            return self.parent().parent().parent().parent().parent().parent().parent().parent().parent().parent().parent()
        except AttributeError:
            if self.exists():
                raise
            else:
                raise RuntimeDraggingError

    def width(self):
        """Override to get docked width."""
        if self.dockable():
            return self._parentOverride(usePane=True).width()
        return super(NukeWindow, self).width()

    def height(self):
        """Override to get docked height."""
        if self.dockable():
            return self._parentOverride(usePane=True).width()
        return super(NukeWindow, self).height()

    def _registerNukeCallbacks(self):
        """Register all legacy callbacks."""
        numEvents = 0
        inst = self.windowInstance()
        if inst is None:
            return 0

        for group in inst['callback'].keys():
            for callbackName, (callbackAdd, callbackRemove) in self._CALLBACKS.items():
                for func in inst['callback'][group][callbackName]:
                    for nodeClass in inst['callback'][group][callbackName][func]:
                        if nodeClass is None:
                            getattr(nuke, callbackAdd)(func)
                        else:
                            getattr(nuke, callbackAdd)(func, nodeClass=nodeClass)
                        numEvents += 1
        return numEvents

    def _unregisterNukeCallbacks(self):
        """Unregister all legacy callbacks."""
        inst = self.windowInstance()
        if inst is None:
            return 0

        numEvents = 0
        for group in inst['callback'].keys():
            for callbackName, (callbackAdd, callbackRemove) in self._CALLBACKS.items():
                for func in inst['callback'][group][callbackName]:
                    for nodeClass in inst['callback'][group][callbackName][func]:
                        if nodeClass is None:
                            getattr(nuke, callbackRemove)(func)
                        else:
                            getattr(nuke, callbackRemove)(func, nodeClass=nodeClass)
                        numEvents += 1
        return numEvents

    def removeCallback(self, func, group=None, nodeClass=None):
        """Remove an individual callback."""
        windowInstance = self.windowInstance()
        if group is None:
            groups = list(windowInstance['callback'].keys())
        else:
            if group not in windowInstance['callback']:
                groups = []
            groups = [group]

        numEvents = 0
        for group in groups:
            for callbackName, (callbackAdd, callbackRemove) in self._CALLBACKS.items():
                if func in windowInstance['callback'][group][callbackName]:
                    for nodeClass in windowInstance['callback'][group][callbackName][func]:
                        if nodeClass is None:
                            if nodeClass is None:
                                getattr(nuke, callbackRemove)(func)
                            else:
                                getattr(nuke, callbackRemove)(func, nodeClass=nodeClass)
                        elif nodeClass == nodeClass:
                            getattr(nuke, callbackRemove)(func, nodeClass=nodeClass)
                        else:
                            continue
                        numEvents += 1
                        del windowInstance['callback'][group][callbackName][func][nodeClass]
        return numEvents

    @hybridmethod
    def removeCallbacks(cls, self, group=None, windowInstance=None, windowID=None):
        """Remove a callback group or all callbacks."""
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
                groups = []
            else:
                groups = [group]

        # Iterate through each callback to remove certain groups
        numEvents = 0
        for group in groups:
            for callbackName, (callbackAdd, callbackRemove) in self._CALLBACKS.items():
                for func in windowInstance['callback'][group][callbackName]:
                    for nodeClass in windowInstance['callback'][group][callbackName][func]:
                        if nodeClass is None:
                            getattr(nuke, callbackRemove)(func)
                        else:
                            getattr(nuke, callbackRemove)(func, nodeClass=nodeClass)
                        numEvents += 1
            del windowInstance['callback'][group]
        return numEvents

    def _addNukeCallbackGroup(self, group):
        windowInstance = self.windowInstance()
        if group in windowInstance['callback']:
            return
        windowInstance['callback'][group] = defaultdict(lambda: defaultdict(set))

    def addCallbackOnUserCreate(self, func, nodeClass=None, group=None):
        """Executed whenever a node is created by the user.
        Not called when loading existing scripts, pasting nodes, or undoing a delete.
        """
        self._addNukeCallbackGroup(group)
        self.windowInstance()['callback'][group]['onUserCreate'][func].add(nodeClass)
        if not self._isHiddenNk:
            if nodeClass is None:
                nuke.addOnUserCreate(func)
            else:
                nuke.addOnUserCreate(func, nodeClass=nodeClass)

    def addCallbackOnCreate(self, func, nodeClass=None, group=None):
        """Executed when any node is created.
        Examples include loading a script (includes new file), pasting a node, selecting a menu item, or undoing a delete.
        """
        self._addNukeCallbackGroup(group)
        self.windowInstance()['callback'][group]['onCreate'][func].add(nodeClass)
        if not self._isHiddenNk:
            if nodeClass is None:
                nuke.addOnCreate(func)
            else:
                nuke.addOnCreate(func, nodeClass=nodeClass)

    def addCallbackOnScriptLoad(self, func, nodeClass=None, group=None):
        """Executed when a script is loaded.
        This will be called by onCreate (for root), and straight after onCreate.
        """
        self._addNukeCallbackGroup(group)
        self.windowInstance()['callback'][group]['onScriptLoad'][func].add(nodeClass)
        if not self._isHiddenNk:
            if nodeClass is None:
                nuke.addOnScriptLoad(func)
            else:
                nuke.addOnScriptLoad(func, nodeClass=nodeClass)

    def addCallbackOnScriptSave(self, func, nodeClass=None, group=None):
        """Executed when the user tries to save a script."""
        self._addNukeCallbackGroup(group)
        self.windowInstance()['callback'][group]['onScriptSave'][func].add(nodeClass)
        if not self._isHiddenNk:
            if nodeClass is None:
                nuke.addOnScriptSave(func)
            else:
                nuke.addOnScriptSave(func, nodeClass=nodeClass)

    def addCallbackOnScriptClose(self, func, nodeClass=None, group=None):
        """Executed when Nuke is exited or the script is closed."""
        self._addNukeCallbackGroup(group)
        self.windowInstance()['callback'][group]['onScriptClose'][func].add(nodeClass)
        if not self._isHiddenNk:
            if nodeClass is None:
                nuke.addOnScriptClose(func)
            else:
                nuke.addOnScriptClose(func, nodeClass=nodeClass)

    def addCallbackOnDestroy(self, func, nodeClass=None, group=None):
        self._addNukeCallbackGroup(group)
        self.windowInstance()['callback'][group]['onDestroy'][func].add(nodeClass)
        if not self._isHiddenNk:
            if nodeClass is None:
                nuke.addOnDestroy(func)
            else:
                nuke.addOnDestroy(func, nodeClass=nodeClass)

    def addCallbackKnobChanged(self, func, nodeClass=None, group=None):
        self._addNukeCallbackGroup(group)
        self.windowInstance()['callback'][group]['knobChanged'][func].add(nodeClass)
        if not self._isHiddenNk:
            if nodeClass is None:
                nuke.addKnobChanged(func)
            else:
                nuke.addKnobChanged(func, nodeClass=nodeClass)

    def addCallbackUpdateUI(self, func, nodeClass=None, group=None):
        self._addNukeCallbackGroup(group)
        self.windowInstance()['callback'][group]['updateUI'][func].add(nodeClass)
        if not self._isHiddenNk:
            if nodeClass is None:
                nuke.addUpdateUI(func)
            else:
                nuke.addUpdateUI(func, nodeClass=nodeClass)

    @classmethod
    def clearWindowInstance(cls, windowID):
        """Close the last class instance."""
        try:
            previousInstance = super(NukeWindow, cls).clearWindowInstance(windowID)
        except TypeError:
            return
        if previousInstance is None:
            return
        cls.removeCallbacks(windowInstance=previousInstance)
        previousInstance['window'].callbacks.unregister()

        #Shut down the window
        if not previousInstance['window'].isClosed():
            try:
                previousInstance['window'].close()
            except (RuntimeError, ReferenceError):
                pass

    def deferred(self, func, *args, **kwargs):
        """Execute a deferred command."""
        def wrapper():
            """Wrap the executed function to display any errors.
            Without this, it will silently fail.
            """
            try:
                func(*args, **kwargs)
            except Exception:
                import traceback
                traceback.print_exc()
        utils.executeDeferred(wrapper)

    def parent(self, *args, **kwargs):
        """Fix a weird Nuke crash.
        It seems to be under a specific set of circumstances, so I'm
        not sure how to deal with it other than with this workaround.

        Details specific to my issue:
            Non-dockable window
            Location data doesn't exist, causing centreWindow to run
            Requesting self.parent() inside centreWindow crashes Nuke.

        This fix runs getMainWindow if loading isn't complete.
        """
        if not self.__useNukeTemporaryParent or self.dockable():
            return super(NukeWindow, self).parent(*args, **kwargs)
        return getMainWindow()

    def hideEvent(self, event):
        """Unregister callbacks and save window location."""
        if not event.spontaneous() and not self.isClosed():
            self._isHiddenNk = True
            self._unregisterNukeCallbacks()
            self.callbacks.unregister()
            self.saveWindowPosition()
        return super(NukeWindow, self).hideEvent(event)

    def showEvent(self, event):
        """Register callbacks and update UI (if checkForChanges is defined)."""
        if not event.spontaneous():
            self._isHiddenNk = False
            self.callbacks.register()
            self._registerNukeCallbacks()
            if hasattr(self, 'checkForChanges'):
                self.checkForChanges()
        return super(NukeWindow, self).showEvent(event)

    def hide(self):
        """Hide the Nuke window."""
        if not self.dockable():
            return super(NukeWindow, self).hide()

    @hybridmethod
    def show(cls, self, *args, **kwargs):
        """Show the Nuke window."""
        # Window is already initialised
        if self is not cls:
            if self.dockable():
                return None
            return super(NukeWindow, self).show()

        #Close down any instances of the window
        try:
            cls.clearWindowInstance(cls.WindowID)
        except AttributeError:
            settings = {}
        else:
            settings = getWindowSettings(cls.WindowID)

        #Load settings
        try:
            nukeSettings = settings[self.application]
        except KeyError:
            nukeSettings = settings[self.application] = {}

        if hasattr(cls, 'WindowDockable'):
            docked = cls.WindowDockable
        else:
            try:
                docked = nukeSettings['docked']
            except KeyError:
                try:
                    docked = cls.WindowDefaults['docked']
                except (AttributeError, KeyError):
                    docked = True

        dockOverride = False
        if docked:
            # Attempt to find the module in the global scope
            # If it can't be found, then it can't be docked
            namespace = searchGlobals(cls)
            if namespace is None:
                docked = cls.WindowDockable = False
                dockOverride = True

        #Return new class instance and show window
        if docked:
            try:
                pane = Pane.get(nukeSettings['dock']['panel']) or Pane.auto()
            except KeyError:
                pane = Pane.auto()

            # Set WindowID if needed but disable saving
            class WindowClass(cls):
                if not hasattr(cls, 'WindowID'):
                    WindowID = uuid.uuid4().hex
                    def enableSaveWindowPosition(self, enable):
                        return super(WindowClass, self).enableSaveWindowPosition(False)

            panel = panels.registerWidgetAsPanel(
                widget=namespace,
                name=getattr(WindowClass, 'WindowName', 'New Window'),
                id=WindowClass.WindowID,
                create=True,
            )
            panel.addToPane(pane)

            panelObject = panel.customKnob.getObject()
            if panelObject is not None:
                widget = panelObject.widget
                _removeMargins(widget)
                widget.deferred(widget.windowReady.emit)
                return widget

        kwargs['dockable'] = False
        win = super(NukeWindow, cls).show(*args, **kwargs)
        if dockOverride:
            cls.WindowDockable = True
            win.setDockable(True, override=True)
        return win

    @classmethod
    def dialog(cls, parent=None, *args, **kwargs):
        """Create the window as a dialog."""
        if parent is None:
            parent = getMainWindow()
        return super(NukeWindow, cls).dialog(parent=parent, *args, **kwargs)

    def updateValue(self):
        """Placeholder method to prevent exceptions when loading docked windows in Nuke 14+.

        This is only an approximate traceback as nothing is actually shown:
            vfxwindow.nuke.NukeWindow.show: panel.addToPane(pane)
            nukescripts.panels.PythonPanel.addToPane: create()
            nukescripts.panels.PythonPanel.create: self.__widget = self.__node.createWidget( self )
            nuke.PanelNode.createWidget: <no source code available>
        """


class NukeBatchWindow(NukeCommon, StandaloneWindow):
    """Variant of the Standalone window for Nuke in batch mode."""

    def __init__(self, *args, **kwargs):
        _checkContextSupported()
        super(NukeBatchWindow, self).__init__(*args, **kwargs)

    def setWindowPalette(self, program, version=None, style=True, force=False):
        if force:
            super(NukeBatchWindow, self).setWindowPalette(program, version, style)

    def saveWindowPosition(self):
        """Save the window location."""
        if self.application in self.windowSettings:
            settings = self.windowSettings[self.application]
        else:
            settings = self.windowSettings[self.application] = {}

        key = self._getSettingsKey()
        if key not in settings:
            settings[key] = {}

        try:
            settings[key]['width'] = self.width()
            settings[key]['height'] = self.height()
            settings[key]['x'] = self.x()
            settings[key]['y'] = self.y()
        except RuntimeDraggingError:
            if not self.dockable():
                raise
        else:
            super(NukeBatchWindow, self).saveWindowPosition()

    def loadWindowPosition(self):
        """Set the position of the window when loaded."""
        try:
            settings = self.windowSettings[self.application][self._getSettingsKey()]
            width = settings['width']
            height = settings['height']
            x = settings['x']
            y = settings['y']
        except KeyError:
            super(NukeBatchWindow, self).loadWindowPosition()
        else:
            x, y = setCoordinatesToScreen(x, y, width, height, padding=5)
            self.resize(width, height)
            self.move(x, y)

    @hybridmethod
    def show(cls, self, *args, **kwargs):
        """Load the window in Nuke batch mode."""
        # Window is already initialised
        if self is not cls:
            return super(NukeBatchWindow, self).show()

        # Close down window if it exists and open a new one
        try:
            cls.clearWindowInstance(cls.WindowID)
        except AttributeError:
            pass
        kwargs['init'] = False
        kwargs['instance'] = True
        kwargs['exec_'] = True
        return super(NukeBatchWindow, cls).show(*args, **kwargs)

    @classmethod
    def dialog(cls, parent=None, *args, **kwargs):
        """Create the window as a dialog."""
        if parent is None:
            parent = getMainWindow()
        return super(NukeWindow, cls).dialog(parent=parent, *args, **kwargs)
