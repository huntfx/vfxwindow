"""Window class for Maya."""

from __future__ import absolute_import, print_function

import uuid
from functools import partial
from Qt import QtWidgets, QtCompat, QtCore

import maya.mel as mel
import maya.cmds as mc
import maya.OpenMayaUI as omUI

from .application import Application
from .callbacks import MayaCallbacks
from ..abstract.gui import AbstractWindow
from ..standalone.gui import StandaloneWindow
from ..utils import hybridmethod, setCoordinatesToScreen, getWindowSettings
from ..utils.gui import forceMenuBar



def getMainWindow(windowID=None, wrapInstance=True):
    """Get pointer to main Maya window.
    The pointer type is a QWidget, so wrap to that (though it can be wrapped to other things too).
    """
    if wrapInstance:
        if windowID is not None:
            pointer = omUI.MQtUtil.findControl(windowID)
        else:
            pointer = omUI.MQtUtil.mainWindow()

        if pointer is not None:
            return QtCompat.wrapInstance(int(pointer), QtWidgets.QWidget)

    # Fallback to searching widgets
    if isinstance(windowID, QtWidgets.QWidget):
        return windowID
    search = windowID or 'MayaWindow'
    for obj in QtWidgets.QApplication.topLevelWidgets():
        if obj.objectName() == search:
            return obj


def deleteWorkspaceControl(windowID, resetFloating=True):
    """Handle deleting a workspaceControl with a particular ID."""
    if mc.workspaceControl(windowID, query=True, exists=True):
        floating = mc.workspaceControl(windowID, query=True, floating=True)
        mc.deleteUI(windowID)
    else:
        floating = None

    #Delete the window preferences (position, size, etc), if the window is not currently floating
    if mc.workspaceControlState(windowID, query=True, exists=True) and (not floating or floating and resetFloating):
        mc.workspaceControlState(windowID, remove=True)

    return floating


def deleteDockControl(windowID):
    """Handle deleting a dockControl with a particular ID."""
    # Get current floating state
    if mc.dockControl(windowID, query=True, exists=True):
        floating = mc.dockControl(windowID, query=True, floating=True)
        mc.dockControl(windowID, edit=True, r=True)
        mc.dockControl(windowID, edit=True, floating=False)
    else:
        floating = None

    # Close down the dock control
    windowWrap = getMainWindow(windowID)
    if windowWrap is not None:
        if windowWrap.parent().parent() is not None:
            getMainWindow(windowID).parent().close()

    if floating is not None:
        try:
            mc.dockControl(windowID, edit=True, floating=floating)
        except RuntimeError:
            pass

    return floating


def workspaceControlWrap(windowClass, dock=True, resetFloating=True, *args, **kwargs):
    """Template class for docking a Qt widget to maya 2017+.
    Requires the window to contain the attributes WindowID and WindowName.

    Source (heavily modified): https://gist.github.com/liorbenhorin/69da10ec6f22c6d7b92deefdb4a4f475
    """
    # Set WindowID if needed but disable saving
    class WindowClass(windowClass):
        if not hasattr(windowClass, 'WindowID'):
            WindowID = uuid.uuid4().hex
            def enableSaveWindowPosition(self, enable):
                return super(WindowClass, self).enableSaveWindowPosition(False)

    # Remove existing window
    floating = deleteWorkspaceControl(WindowClass.WindowID, resetFloating=resetFloating)
    if not resetFloating and floating is None:
        floating = not dock

    # Setup Maya's window
    if dock:
        defaultDock = mel.eval('getUIComponentDockControl("Attribute Editor", false)')
        if isinstance(dock, (bool, int)):
            dock = defaultDock
        try:
            mc.workspaceControl(WindowClass.WindowID, retain=True, label=getattr(WindowClass, 'WindowName', 'New Window'), tabToControl=[dock, -1])
        except RuntimeError:
            deleteWorkspaceControl(WindowClass.WindowID, resetFloating=resetFloating)
            mc.workspaceControl(WindowClass.WindowID, retain=True, label=getattr(WindowClass, 'WindowName', 'New Window'), tabToControl=[defaultDock, -1])
    else:
        mc.workspaceControl(WindowClass.WindowID, retain=True, label=getattr(WindowClass, 'WindowName', 'New Window'), floating=True)

    # Setup main window and parent to Maya
    workspaceControlWin = getMainWindow(WindowClass.WindowID)
    workspaceControlWin.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    windowInstance = WindowClass(parent=workspaceControlWin, dockable=True, *args, **kwargs)
    forceMenuBar(windowInstance)

    # Attach callbacks
    windowInstance.signalConnect(workspaceControlWin.destroyed, windowInstance.close, group='__mayaDockWinDestroy')
    try:
        mc.workspaceControl(WindowClass.WindowID, edit=True, visibleChangeCommand=windowInstance.visibleChangeEvent)
    except (AttributeError, TypeError):
        pass
    try:
        windowInstance.loadWindowPosition()
    except (AttributeError, TypeError):
        pass

    # Restore the window (after maya is ready) since it may not be visible
    windowInstance.deferred(windowInstance.windowReady.emit)
    return windowInstance


def dockControlWrap(windowClass, dock=True, *args, **kwargs):

    def attachToDockControl(windowInstance, dock=True, area='right'):
        """This needs to be deferred as it can run before the previous dockControl has closed."""
        if isinstance(dock, (bool, int)):
            dock = 'right'
        if not windowInstance.objectName():
            windowInstance.setObjectName(windowInstance.WindowID)
        mc.dockControl(windowInstance.WindowID, area=dock, floating=False, retain=False, content=windowInstance.objectName(), closeCommand=windowInstance.close)

        windowInstance.setDocked(dock)
        try:
            mc.dockControl(windowInstance.WindowID, edit=True, floatChangeCommand=windowInstance.saveWindowPosition)
        except (AttributeError, TypeError):
            pass

        try:
            windowInstance.deferred(windowInstance.loadWindowPosition)
        except (AttributeError, TypeError):
            pass

        windowInstance.setWindowTitle(getattr(windowInstance, 'WindowName', 'New Window'))
        windowInstance.deferred(windowInstance.windowReady.emit)

    # Set WindowID if needed but disable saving
    class WindowClass(windowClass):
        if not hasattr(windowClass, 'WindowID'):
            WindowID = uuid.uuid4().hex
            def enableSaveWindowPosition(self, enable):
                return super(WindowClass, self).enableSaveWindowPosition(False)

    # Remove existing window
    deleteDockControl(WindowClass.WindowID)

    # Setup main window and parent to Maya
    mayaWin = getMainWindow(wrapInstance=False)
    windowInstance = WindowClass(parent=mayaWin, dockable=True, *args, **kwargs)
    forceMenuBar(windowInstance)
    windowInstance.deferred(partial(attachToDockControl, windowInstance, dock))

    # Restore the window (after maya is ready) since it may not be visible
    return windowInstance


class MayaCommon(object):

    CallbackClass = MayaCallbacks

    @property
    def application(self):
        """Get the current application."""
        return Application

    def deferred(self, func, *args, **kwargs):
        """Execute a deferred command."""
        mc.evalDeferred(func, *args, **kwargs)


class MayaWindow(MayaCommon, AbstractWindow):
    """Window to use for Maya.

    This is an alternative to maya.app.general.mayaMixin.MayaQWidgetDockableMixin, as many features
    were already implemented when I found it, and is also missing a few parts I would have liked.

    The checks against Maya 2017 are because `workspaceControl` was
    added at that point.
    """

    def __init__(self, parent=None, dockable=False, **kwargs):
        if parent is None:
            parent = getMainWindow()
        super(MayaWindow, self).__init__(parent, **kwargs)
        self.setDockable(dockable, override=True)

        # The line below can save the window preferences, but this window automatically does it
        #self.setProperty("saveWindowPref", True)

        self.__parentTemp = None

    def visibleChangeEvent(self, *args, **kwargs):
        """The window may have been docked/undocked.

        If floating, then first load the previous position, since there
        is no hook for this elsewhere.
        Both modes will then save the position, which will either store
        the control name for docked windows, or the coordinates for
        floating ones.

        This is not super efficient and only works if the window hasn't
        been closed, but it helps keep the correct location state.
        """
        if self.dockable():
            if self.floating():
                # Load the correct location only if previously docked
                # If this ran all the time, then the window will
                # minimise and restore to a different location, and
                # completely fail to maximise
                if not self.windowSettings.get('maya', {}).get('dock', {}).get('floating', True):
                    self.loadWindowPosition()

                # Maya dockControl and workspaceControl works by dynamically creating a QWidget and parent the
                # window to it when it's detached. When attached, the window is docked and the widget destroyed.
                # Maya set it's own window icon to this widget by default, this will just make sure that if the user
                # used a custom icon for it's tool, it's set on the dynamically created floating widget.
                self.setWindowIcon(self.windowIcon())

            self.saveWindowPosition()

    def setWindowIcon(self, icon):
        super(MayaWindow, self).setWindowIcon(icon)
        self._parentOverride().setWindowIcon(icon)

    def closeEvent(self, event):
        """Handle the class being deleted."""
        dockable = self.dockable()
        if not dockable:
            self.saveWindowPosition()
        elif Application.version < 2017:
            try:
                self.saveWindowPosition()
            except TypeError:
                pass

        self.clearWindowInstance(self.WindowID, deleteWindow=True)

        # If dockControl is being used, then Maya will crash if close is called
        if dockable and Application.version < 2017:
            event.ignore()
        else:
            return super(MayaWindow, self).closeEvent(event)

    def exists(self):
        if self.dockable():
            if Application.version < 2017:
                return mc.dockControl(self.WindowID, query=True, exists=True)
            return mc.workspaceControl(self.WindowID, query=True, exists=True)
        return not self.isClosed()

    def raise_(self):
        if self.dockable():
            if Application.version < 2017:
                return mc.dockControl(self.WindowID, edit=True, r=True)
            return mc.workspaceControl(self.WindowID, edit=True, restore=True)
        return super(MayaWindow, self).raise_()

    def setWindowTitle(self, title):
        if self.dockable():
            try:
                if Application.version < 2017:
                    return mc.dockControl(self.WindowID, edit=True, label=title)
                return mc.workspaceControl(self.WindowID, edit=True, label=title)
            except RuntimeError:
                pass
        return super(MayaWindow, self).setWindowTitle(title)

    def isVisible(self):
        if self.dockable():
            try:
                if Application.version < 2017:
                    return mc.dockControl(self.WindowID, query=True, visible=True)
                return mc.workspaceControl(self.WindowID, query=True, visible=True)
            except RuntimeError:
                return False
        return super(MayaWindow, self).isVisible()

    def dockable(self, *args, **kwargs):
        """Catch an error caused if dockable is called too early.
        At this point it doesn't matter if it is dockable or not.
        """
        try:
            return super(MayaWindow, self).dockable(*args, **kwargs)
        except (AttributeError, TypeError):
            return False

    def setDocked(self, dock):
        if self.dockable() and self.floating() == dock:
            if Application.version < 2017:
                self.raise_()
                mc.dockControl(self.WindowID, edit=True, floating=not dock)
                self.raise_()

            # Dock to the previous control if possible, otherwise the attribute editor
            elif dock:
                self.saveWindowPosition()  # It doesn't automatically save
                try:
                    control = self.windowSettings[self.application]['dock']['control']
                    if control is None:
                        raise KeyError
                except KeyError:
                    control = mel.eval('getUIComponentDockControl("Attribute Editor", false)')
                mc.workspaceControl(self.WindowID, edit=True, tabToControl=[control, -1])
                self.raise_()

            # Undock and make floating
            else:
                mc.workspaceControl(self.WindowID, edit=True, floating=True)
                self.loadWindowPosition()

    def setWindowPalette(self, program, version=None, style=True, force=False):
        """Set the palette of the window.
        This will cause issues in the Maya GUI so it's disabled by default.
        The force parameter can be set to override this behaviour.
        """
        if force or self.application.batch:
            super(MayaWindow, self).setWindowPalette(program, version, style)

    def windowPalette(self):
        """Get the current window palette."""
        currentPalette = super(MayaWindow, self).windowPalette()
        if currentPalette is None:
            return 'Maya.{}'.format(int(Application.version))
        return currentPalette

    def _parentOverride(self):
        """Get the correct parent needed to query window data.
        It needs to be set to an attribute or Python will forget the C++ pointer.

        Known Issues:
            - Creating a new dock by hand will result in an error saying
                the `QTabWidget` has already been deleted when reading
                information from the parent widget. Running it again is
                totally fine however, and I wasn't able to figure out
                how to fix. For most purposes this shouldn't affect
                anyone, as the window is incapable of making a new dock
                widget and can only restore to an existing one.
        """
        if Application.version < 2017:
            return self.parent()

        #Determine if it's a new window, we need to get the C++ pointer again
        if self.__parentTemp is None:
            base = getMainWindow(self.WindowID)
        else:
            base = self.parent()

        if base is None:
            # If the window has no parent, it was probably forgotten by user so we can
            # assume it should be the maya main window.
            self.__parentTemp = super(MayaWindow, self)._parentOverride()
        else:
            #Get the correct parent level
            if self.floating():
                self.__parentTemp = base.parent().parent().parent().parent()
            else:
                self.__parentTemp = base.parent().parent()

        return self.__parentTemp

    def floating(self):
        """Return if the window is floating."""
        if not self.dockable():
            return False
        if Application.version < 2017:
            return mc.dockControl(self.WindowID, query=True, floating=True)
        return mc.workspaceControl(self.WindowID, query=True, floating=True)

    def resize(self, width, height=None):
        """Resize the window."""
        if isinstance(width, QtCore.QSize):
            height = width.height()
            width = width.width()
        if self.dockable():
            if Application.version < 2017:
                if not self.floating():
                    return mc.dockControl(self.WindowID, edit=True, width=width, height=height)
            else:
                return mc.workspaceControl(self.WindowID, edit=True, resizeWidth=width, resizeHeight=height)
        return super(MayaWindow, self).resize(width, height)

    def siblings(self):
        """Find other widgets in the same tag group."""
        if self.dockable():
            if Application.version < 2017:
                return []
            return self.parent().parent().children()
        return []

    if Application.version < 2017:
        def area(self, *args, **kwargs):
            """Return the Maya area name."""
            return mc.dockControl(self.WindowID, query=True, area=True)

    else:
        def control(self, *args, **kwargs):
            """Return the Maya Control name, so it can be attached again."""
            if not self.dockable():
                return None

            workspaces = [
                mel.eval('$gViewportWorkspaceControl=$gViewportWorkspaceControl'),
                mel.eval('getUIComponentDockControl("Tool Settings", false)'),
                mel.eval('getUIComponentDockControl("Attribute Editor", false)'),
                mel.eval('getUIComponentDockControl("Channel Box", false)'),
                mel.eval('getUIComponentDockControl("Layer Editor", false)'),
                mel.eval('getUIComponentDockControl("Channel Box / Layer Editor", false)'),
                mel.eval('getUIComponentDockControl("Outliner", false)'),
                mel.eval('getUIComponentToolBar("Shelf", false)'),
                mel.eval('getUIComponentToolBar("Time Slider", false)'),
                mel.eval('getUIComponentToolBar("Range Slider", false)'),
                mel.eval('getUIComponentToolBar("Command Line", false)'),
                mel.eval('getUIComponentToolBar("Help Line", false)'),
                mel.eval('getUIComponentToolBar("Tool Box", false)'),
                'UVToolkitDockControl',
                'polyTexturePlacementPanel1Window',
                'hyperGraphPanel1Window',
                'graphEditor1Window',
                'timeEditorPanel1Window',
                'nodeEditorPanel1Window',
                'shapePanel1Window',
                'posePanel1Window',
                'hyperShadePanel1Window',
                'contentBrowserPanel1Window',
                'outlinerPanel1Window',
                'clipEditorPanel1Window',
                'devicePanel1Window',
                'dynPaintScriptedPanelWindow',
                'blindDataEditor1Window',
            ]
            stackedWidget = self.parent().parent()
            for control in workspaces:
                widget = getMainWindow(control)
                if widget is not None:
                    if widget.parent() is stackedWidget:
                        return control

            # Search through siblings until another widget is found
            # TODO: Limit to Maya only widgets (this is why the code above is preferred)
            parent = self.parent()
            for item in self.siblings():
                if item != parent and type(item) == QtWidgets.QWidget:
                    try:
                        return item.objectName()
                    except RuntimeError:
                        pass

            return None

    def centreWindow(self):
        """Centre the window using geometry of the main Maya window."""
        if self.dockable():
            try:
                parentGeometry = self._parentOverride().parent().frameGeometry()
            except RuntimeError:
                return None
        else:
            parentGeometry = None
        return super(MayaWindow, self).centreWindow(parentGeometry=parentGeometry)

    def saveWindowPosition(self):
        """Save the window location."""
        if self.application in self.windowSettings:
            settings = self.windowSettings[self.application]
        else:
            settings = self.windowSettings[self.application] = {}

        settings['docked'] = self.dockable(raw=True)

        key = self._getSettingsKey()
        if key not in settings:
            settings[key] = {}

        dockable = self.dockable()
        try:
            # Save extra docked settings
            if dockable:
                settings[key]['floating'] = self.floating()
                if Application.version < 2017:
                    settings[key]['area'] = self.area()
                else:
                    settings[key]['control'] = self.control() or settings[key].get('control')

            # Only save position if floating
            if not dockable or settings[key]['floating']:
                settings[key]['width'] = self.width()
                settings[key]['height'] = self.height()
                settings[key]['x'] = self.x()
                settings[key]['y'] = self.y()

        # A RuntimeError will occur if a dockable window is being deleted
        except RuntimeError:
            if not dockable:
                raise

        # Need to check again, perhaps this can happen on startup
        except AttributeError:
            pass

        else:
            super(MayaWindow, self).saveWindowPosition()

    def loadWindowPosition(self):
        """Set the position of the window when loaded."""
        try:
            settings = self.windowSettings[self.application][self._getSettingsKey()]
            x = settings['x']
            y = settings['y']
            width = settings['width']
            height = settings['height']
        except KeyError:
            super(MayaWindow, self).loadWindowPosition()
        else:
            x, y = setCoordinatesToScreen(x, y, width, height, padding=5)
            self.resize(width, height)
            self.move(x, y)

    def centralWidget(self):
        """Get the central widget."""
        if self.dockable():
            item = self.parent().layout().itemAt(0)
            if item is not None:
                return item.widget()
        return super(MayaWindow, self).centralWidget()

    def setCentralWidget(self, widget):
        """Set the central widget."""
        if self.dockable():
            self.parent().layout().takeAt(0)
            return self.parent().layout().addWidget(widget)
        return super(MayaWindow, self).setCentralWidget(widget)

    @classmethod
    def clearWindowInstance(cls, windowID, deleteWindow=True):
        """Close the last class instance."""
        previousInstance = super(MayaWindow, cls).clearWindowInstance(windowID)
        if previousInstance is None:
            return
        previousInstance['window'].callbacks.unregister()

        # Disconnect the destroyed signal
        if previousInstance['window'].dockable():
            previousInstance['window'].signalDisconnect('__mayaDockWinDestroy')

        # Shut down the window
        if not previousInstance['window'].isClosed():
            try:
                previousInstance['window'].close()
            except (RuntimeError, ReferenceError):
                pass

        # Deleting the window is disabled by default
        # because it will also delete the window location
        # It's better to handle it elsewhere if possible
        if deleteWindow and previousInstance['window'].dockable():
            if Application.version < 2017:
                deleteDockControl(previousInstance['window'].WindowID)
            else:
                deleteWorkspaceControl(previousInstance['window'].WindowID)
        return previousInstance

    def setFocus(self):
        """Force Maya to focus on the window."""
        if self.dockable():
            return mc.setFocus(self.WindowID)
        return super(MayaWindow, self).setFocus()

    def hide(self):
        """Hide the window."""
        if self.dockable():
            if Application.version < 2017:
                return mc.dockControl(self.WindowID, edit=True, visible=False)
            self.parent().setAttribute(QtCore.Qt.WA_DeleteOnClose, False)
            return mc.workspaceControl(self.WindowID, edit=True, visible=False)
        return super(MayaWindow, self).hide()

    @hybridmethod
    def show(cls, self, *args, **kwargs):
        """Show the Maya window.
        It can be as a docked or floating workspaceControl, or just a normal Qt window.
        """
        if self is not cls:
            # Case where window is already initialised
            if self.dockable():
                if Application.version < 2017:
                    return mc.dockControl(self.WindowID, edit=True, visible=True)
                result = mc.workspaceControl(self.WindowID, edit=True, visible=True)
                self.parent().setAttribute(QtCore.Qt.WA_DeleteOnClose)
                return result
            return super(MayaWindow, self).show()

        # Close down any instances of the window
        try:
            cls.clearWindowInstance(cls.WindowID)
        except AttributeError:
            settings = {}
        else:
            settings = getWindowSettings(cls.WindowID)

        # Load settings
        try:
            mayaSettings = settings[Application]
        except KeyError:
            mayaSettings = settings[Application] = {}

        if hasattr(cls, 'WindowDockable'):
            docked = cls.WindowDockable
        else:
            try:
                docked = mayaSettings['docked']
            except KeyError:
                try:
                    docked = cls.WindowDefaults['docked']
                except (AttributeError, KeyError):
                    docked = True

        # Override docked mode in case of mayabatch
        batchOverride = False
        if docked and Application.batch:
            docked = cls.WindowDockable = False
            batchOverride = True

        # Return new class instance and show window
        if docked and not batchOverride:
            if hasattr(cls, 'WindowDocked'):
                floating = not cls.WindowDocked
            else:
                try:
                    floating = mayaSettings['dock']['floating']
                except KeyError:
                    try:
                        floating = cls.WindowDefaults['floating']
                    except (AttributeError, KeyError):
                        floating = False
            if floating:
                dock = False
            else:
                try:
                    if Application.version < 2017:
                        dock = mayaSettings['dock'].get('area', True)
                    else:
                        dock = mayaSettings['dock'].get('control', True)
                except KeyError:
                    dock = True

            if Application.version < 2017:
                return dockControlWrap(cls, dock,  *args, **kwargs)
            return workspaceControlWrap(cls, dock, True, *args, **kwargs)

        win = super(MayaWindow, cls).show(*args, **kwargs)
        if batchOverride:
            cls.WindowDockable = True
            win.setDockable(True, override=True)
        return win


class MayaBatchWindow(MayaCommon, StandaloneWindow):
    """Variant of the Standalone window for Maya in batch mode.
    While MayaWindow could be used, it can't be automatically setup.
    """

    def saveWindowPosition(self):
        """Save the window location."""
        if self.application not in self.windowSettings:
            self.windowSettings[self.application] = {}
        settings = self.windowSettings[self.application]

        key = self._getSettingsKey()
        if key not in settings:
            settings[key] = {}

        settings[key]['width'] = self.width()
        settings[key]['height'] = self.height()
        settings[key]['x'] = self.x()
        settings[key]['y'] = self.y()

        super(MayaBatchWindow, self).saveWindowPosition()

    def loadWindowPosition(self):
        """Set the position of the window when loaded."""
        try:
            settings = self.windowSettings[self.application][self._getSettingsKey()]
            width = settings['width']
            height = settings['height']
            x = settings['x']
            y = settings['y']
        except KeyError:
            super(MayaBatchWindow, self).loadWindowPosition()
        else:
            x, y = setCoordinatesToScreen(x, y, width, height, padding=5)
            self.resize(width, height)
            self.move(x, y)

    @hybridmethod
    def show(cls, self, *args, **kwargs):
        """Load the window in Maya batch mode.

        The QApplication MUST be initialised before pymel.core, since
        pymel sets up a fake application. This is done automatically
        in vfxwindow/__init__.py, since at the time of calling this
        method, it is already too late.
        Once the window has been created, it can be shown with
        QApplication.instance().exec_(). If the QApplication has not
        been successfully set up, it will complain that it's not able
        to create a widget without a QApplication.
        See: https://help.autodesk.com/cloudhelp/2018/JPN/Maya-Tech-Docs/PyMel/standalone.html
        """
        # Window is already initialised
        if self is not cls:
            return super(MayaBatchWindow, self).show()

        # Close down window if it exists and open a new one
        try:
            cls.clearWindowInstance(cls.WindowID)
        except AttributeError:
            pass
        kwargs['instance'] = True
        kwargs['exec_'] = True
        return super(MayaBatchWindow, cls).show(*args, **kwargs)
