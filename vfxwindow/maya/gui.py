"""Window class for Maya."""

from __future__ import absolute_import, print_function

import uuid
from functools import partial
from Qt import QtWidgets, QtCompat, QtCore

import maya.mel as mel
import maya.cmds as mc
import maya.OpenMaya as om
import maya.OpenMayaUI as omUI
import maya.api.OpenMaya as om2

from .application import Application
from .callbacks import MayaCallbacks
from ..abstract.gui import AbstractWindow
from ..standalone.gui import StandaloneWindow
from ..utils import hybridmethod, setCoordinatesToScreen, getWindowSettings, deprecate
from ..utils.gui import forceMenuBar


# Map each function required for each callback
SCENE_CALLBACKS = {
    None: om2.MSceneMessage.addCallback,  # Default option
    om2.MSceneMessage.kBeforeNewCheck: om2.MSceneMessage.addCheckCallback,
    om2.MSceneMessage.kBeforeImportCheck: om2.MSceneMessage.addCheckCallback,
    om2.MSceneMessage.kBeforeOpenCheck: om2.MSceneMessage.addCheckCallback,
    om2.MSceneMessage.kBeforeExportCheck: om2.MSceneMessage.addCheckCallback,
    om2.MSceneMessage.kBeforeSaveCheck: om2.MSceneMessage.addCheckCallback,
    om2.MSceneMessage.kBeforeCreateReferenceCheck: om2.MSceneMessage.addCheckCallback,
    om2.MSceneMessage.kBeforeLoadReferenceCheck: om2.MSceneMessage.addCheckCallback,
    om2.MSceneMessage.kBeforeImportCheck: om2.MSceneMessage.addCheckFileCallback,
    om2.MSceneMessage.kBeforeOpenCheck: om2.MSceneMessage.addCheckFileCallback,
    om2.MSceneMessage.kBeforeExportCheck: om2.MSceneMessage.addCheckFileCallback,
    om2.MSceneMessage.kBeforeCreateReferenceCheck: om2.MSceneMessage.addCheckFileCallback,
    om2.MSceneMessage.kBeforeLoadReferenceCheck: om2.MSceneMessage.addCheckFileCallback,
    om2.MSceneMessage.kBeforePluginLoad: om2.MSceneMessage.addStringArrayCallback,
    om2.MSceneMessage.kAfterPluginLoad: om2.MSceneMessage.addStringArrayCallback,
    om2.MSceneMessage.kBeforePluginUnload: om2.MSceneMessage.addStringArrayCallback,
    om2.MSceneMessage.kAfterPluginUnload: om2.MSceneMessage.addStringArrayCallback,
}


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
    workspaceControlWin = kwargs['parent'] = getMainWindow(WindowClass.WindowID)
    workspaceControlWin.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    windowInstance = WindowClass(dockable=True, *args, **kwargs)
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


def toMObject(node):
    """Convert a node to an MObject."""
    if isinstance(node, om2.MObject):
        return node
    selected = om2.MSelectionList()
    try:
        selected.add(str(node))
    except RuntimeError:
        return None
    return selected.getDependNode(0)


class MayaCommon(object):

    def _createCallbackHandler(self):
        """Create the callback handler.
        For convenience, the "legacy" API group has been created.
        """
        callbacks = MayaCallbacks(self)
        callbacks['legacy'].api = om
        return callbacks

    @property
    def application(self):
        """Get the current application."""
        return Application

    def deferred(self, func, *args, **kwargs):
        """Execute a deferred command.
        If the window is a dialog, then execute now as Maya will pause.
        """
        if self.isDialog():
            return func()
        else:
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

    def displayMessage(self, title, message, details=None, buttons=('Ok',), defaultButton=None, cancelButton=None, checkBox=None):
        """This is basically Maya's copy of a QMessageBox."""
        if checkBox is None:
            return mc.confirmDialog(
                title=title,
                message=message,
                button=buttons,
                defaultButton=defaultButton,
                cancelButton=cancelButton,
                dismissString=cancelButton,
            )
        return super(MayaWindow, self).displayMessage(
            title=title,
            message=message,
            buttons=buttons,
            defaultButton=defaultButton,
            cancelButton=cancelButton,
            checkBox=checkBox,
        )

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

    @hybridmethod
    def _removeCallbacks(cls, self, group=None, windowInstance=None, windowID=None):
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

        # Iterate through each callback to remove certain groups
        numEvents = 0
        for group in groups:
            for callbackID in windowInstance['callback'][group]['event']:
                try:
                    om2.MMessage.removeCallback(callbackID)
                except RuntimeError:
                    pass
                else:
                    numEvents += 1
            for callbackID in windowInstance['callback'][group]['node']:
                try:
                    om2.MNodeMessage.removeCallback(callbackID)
                except RuntimeError:
                    pass
                else:
                    numEvents += 1
            for callbackID in windowInstance['callback'][group]['scene']:
                try:
                    om2.MSceneMessage.removeCallback(callbackID)
                except RuntimeError:
                    pass
                else:
                    numEvents += 1
            for callbackID in windowInstance['callback'][group]['job']:
                try:
                    mc.scriptJob(kill=callbackID)
                except RuntimeError:
                    pass
                else:
                    numEvents += 1
            del windowInstance['callback'][group]
        return numEvents

    @hybridmethod
    @deprecate
    def removeCallbacks(cls, self, group=None, windowInstance=None, windowID=None):
        """Remove all the registered callbacks.
        If group is not set, then all will be removed.

        Either windowInstance or windowID is needed if calling without a class instance.
        """
        self._removeCallbacks(group, windowInstance, windowID)

    def _addMayaCallbackGroup(self, group):
        windowInstance = self.windowInstance()
        if group in windowInstance['callback']:
            return
        windowInstance['callback'][group] = {
            'event': [],
            'node': [],
            'scene': [],
            'job': [],
        }

    @deprecate
    def addCallbackEvent(self, callback, func, clientData=None, group=None):
        """Add an event callback.
        Some of the common ones are timeChanged, SelectionChanged, Undo and Redo.

        Parameters:
            callback (str)
            func
            clientData
            group

        Returns:
            clientData

        See Also:
            om2.MEventMessage.getEventNames()
        """
        self._addMayaCallbackGroup(group)
        self.windowInstance()['callback'][group]['event'].append(om2.MEventMessage.addEventCallback(callback, func, clientData))

    def _addCallbackNode(self, callback, node, func, clientData=None, group=None):
        """Add an MNodeMessage callback.
        For internal use to skip the deprecation warning.
        """
        mobj = toMObject(node)
        if mobj is not None:
            self._addMayaCallbackGroup(group)
            self.windowInstance()['callback'][group]['node'].append(callback(mobj, func, clientData))

    @deprecate
    def addCallbackNode(self, callback, node, func, clientData=None, group=None):
        """Add an MNodeMessage callback.
        The callback must be an MNodeMessage function.

        Parameters:
            callback (OpenMaya.MNodeMessage)
            node (OpenMaya.MObject)
            func
            clientData
            group

        Returns:
            msg (int): Use this for bitwise operations with MNodeMessage attributes
            plug (OpenMaya.MPlug): Information on the attribute. plug.name() is 'object.attribute'.
            otherPlug (OpenMaya.MPlug)
            clientData

        See Also:
            https://help.autodesk.com/view/MAYAUL/2016/ENU/?guid=__py_ref_class_open_maya_1_1_m_node_message_html
        """
        return self._addCallbackNode(callback, node, func, clientData, group)

    @deprecate
    def addCallbackAttributeChange(self, node, func, clientData=None, group=None):
        """Add an MNodeMessage callback for when an attribute changes.

        Official Documentation:
            Attribute Changed messages will not be generated while Maya
            is either in playback or scrubbing modes. If you need to do
            something during playback or scrubbing you will have to register
            a callback for the timeChanged message which is the only
            message that is sent during those modes.
        See MayaWindow.addCallbackNode for details.
        """
        self._addCallbackNode(om2.MNodeMessage.addAttributeChangedCallback, node, func, clientData, group=group)

    @deprecate
    def addCallbackAttributeAddOrRemove(self, node, func, clientData=None, group=None):
        """Add an MNodeMessage callback for when an attribute is added.

        Official Documentation:
            This is a more specific version of addAttributeChanged as only attribute
            added and attribute removed messages will trigger the callback.
        See MayaWindow.addCallbackNode for details.
        """
        self._addCallbackNode(om2.MNodeMessage.addAttributeAddedOrRemovedCallback, node, func, clientData, group=group)

    @deprecate
    def addCallbackNodeRename(self, node, func, clientData=None, group=None):
        """Add an MNodeMessage callback for when a node is renamed.

        See MayaWindow.addCallbackNode for details.
        """
        self._addCallbackNode(om2.MNodeMessage.addNameChangedCallback, node, func, clientData, group=group)

    @deprecate
    def addCallbackNodeDirty(self, node, func, clientData=None, group=None):
        """Add an MNodeMessage callback for node dirty messages.

        See MayaWindow.addCallbackNode for details.
        """

        self._addCallbackNode(om2.MNodeMessage.addNodeDirtyCallback, node, func, clientData, group=group)

    @deprecate
    def addCallbackNodeDirtyPlug(self, node, func, clientData=None, group=None):
        """Add an MNodeMessage callback for node dirty messages.

        Official Documentation:
            This callback provides the plug on the node that was dirtied.
            Only provides dirty information on input plugs.
        See MayaWindow.addCallbackNode for details.
        """
        self._addCallbackNode(om2.MNodeMessage.addNodeDirtyPlugCallback, node, func, clientData, group=group)

    @deprecate
    def addCallbackUuidChange(self, node, func, clientData=None, group=None):
        """Add an MNodeMessage callback for when a node UUID is changed.

        See MayaWindow.addCallbackNode for details.
        """
        self._addCallbackNode(om2.MNodeMessage.addUuidChangedCallback, node, func, clientData, group=group)

    @deprecate
    def addCallbackKeyableChange(self, node, func, clientData=None, group=None):
        """Add an MNodeMessage callback for when the keyable state of a node is changed.

        Official Documentation:
            This method registers a callback that is invoked by any class that
            changes the keyable state of an attribute. When the callback is
            invoked, the API programmer can make a decision on how to handle
            the given keyable change event. The programmer can either accept
            the keyable state change by returning True.
            or reject it by returning False.

            Note: you can only attach one callback keyable change override
            callback per attribute. It is an error to attach more than one
            callback to the same attribute.
        See MayaWindow.addCallbackNode for details.
        """
        self._addCallbackNode(om2.MNodeMessage.addKeyableChangeOverride, node, func, clientData, group=group)

    @deprecate
    def addCallbackNodeRemove(self, node, func, clientData=None, group=None):
        """Add an MNodeMessage callback for when a node is deleted.
        This uses addNodePreRemovalCallback instead of addNodeAboutToDeleteCallback as it shouldn't
        be removed if the node is deleted (eg. if the deletion is undone).

        Official Documentation:
            This callback is called before connections on the node are removed.
            Unlike the aboutToDelete callback, this callback will be invoked whenever
            the node is deleted, even during a redo.
            Note that this callback method should not perform any DG operations.
        See MayaWindow.addCallbackNode for details.
        """
        self._addCallbackNode(om2.MNodeMessage.addNodePreRemovalCallback, node, func, clientData, group=group)

    @deprecate
    def addCallbackScene(self, callback, func, clientData=None, group=None):
        """Add a scene callback.

        Returns:
            clientData

        Notable Callbacks:
            kBeforeNew / kAfterNew
            kBeforeOpen / kAfterOpen
            kBeforeSave / kAfterSave

        See Also:
            http://download.autodesk.com/us/maya/2011help/api/class_m_scene_message.html
        """
        self._addMayaCallbackGroup(group)
        if not isinstance(callback, int):
            callback = getattr(om2.MSceneMessage, callback)

        apiFunction = SCENE_CALLBACKS.get(callback, SCENE_CALLBACKS[None])
        self.windowInstance()['callback'][group]['scene'].append(apiFunction(callback, func, clientData))

    @deprecate
    def addCallbackJobEvent(self, callback, func, group=None, runOnce=False):
        self._addMayaCallbackGroup(group)
        self.windowInstance()['callback'][group]['job'].append(mc.scriptJob(runOnce=runOnce, event=[callback, func]))

    @deprecate
    def addCallbackJobCondition(self, callback, func, group=None, runOnce=False):
        self._addMayaCallbackGroup(group)
        self.windowInstance()['callback'][group]['job'].append(mc.scriptJob(runOnce=runOnce, conditionChange=[callback, func]))

    @deprecate
    def addCallbackNodeTypeAdd(self, func, nodeType='dependNode', clientData=None, group=None):
        """Add an MDGMessage callback for whenever a new node is added to the dependency graph."""
        self._addMayaCallbackGroup(group)
        self.windowInstance()['callback'][group]['event'].append(om2.MDGMessage.addNodeAddedCallback(func, nodeType, clientData))

    @deprecate
    def addCallbackNodeTypeRemove(self, func, nodeType='dependNode', clientData=None, group=None):
        """Add an MDGMessage callback for whenever a new node is removed from the dependency graph.
        This is used instead of addNodeDestroyedCallback since nodes are not instantly destroyed.
        """
        self._addMayaCallbackGroup(group)
        self.windowInstance()['callback'][group]['event'].append(om2.MDGMessage.addNodeRemovedCallback(func, nodeType, clientData))

    @deprecate
    def addCallbackTimeChange(self, func, clientData=None, group=None):
        """Add an MDGMessage callback for whenever the time changes in the dependency graph."""

        self._addMayaCallbackGroup(group)
        self.windowInstance()['callback'][group]['event'].append(om2.MDGMessage.addTimeChangeCallback(func, clientData))

    @deprecate
    def addCallbackForceUpdate(self, func, clientData=None, group=None):
        """Add an MDGMessage callback for after the time changes and after all nodes have been evaluated in the dependency graph."""
        self._addMayaCallbackGroup(group)
        self.windowInstance()['callback'][group]['event'].append(om2.MDGMessage.addForceUpdateCallback(func, clientData))

    @deprecate
    def addCallbackConnectionAfter(self, func, clientData=None, group=None):
        """Add an MDGMessage callback for after a connection is made or broken in the dependency graph."""
        self._addMayaCallbackGroup(group)
        self.windowInstance()['callback'][group]['event'].append(om2.MDGMessage.addConnectionCallback(func, clientData))

    @deprecate
    def addCallbackConnectionBefore(self, func, clientData=None, group=None):
        """Add an MDGMessage callback for before a connection is made or broken in the dependency graph."""
        self._addMayaCallbackGroup(group)
        self.windowInstance()['callback'][group]['event'].append(om2.MDGMessage.addPreConnectionCallback(func, clientData)(func, clientData))

    @classmethod
    def clearWindowInstance(cls, windowID, deleteWindow=True):
        """Close the last class instance."""
        previousInstance = super(MayaWindow, cls).clearWindowInstance(windowID)
        if previousInstance is None:
            return
        cls._removeCallbacks(windowInstance=previousInstance)
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
        # If a dialog was opened, then the reference will no longer exist
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

    @classmethod
    def dialog(cls, parent=None, *args, **kwargs):
        """Create the window as a dialog.
        For Maya versions after 2017, mc.layoutDialog is used.
        """
        # This is quite buggy and can lock up Maya, so disable for now
        # The issue is likely related to what `setParent` returns.
        if False and Application.version >= 2017:
            # Note: Due to Python 2 limitations, *args and **kwargs can't be unpacked with the
            # title keyword present, so don't try to clean up the code by enabling unpacking again.
            def uiScript(cls, clsArgs=(), clsKwargs={}):
                form = mc.setParent(query=True)
                parent = getMainWindow(form)
                parent.layout().setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

                windowInstance = cls(parent, *clsArgs, **clsKwargs)
                windowInstance.windowReady.emit()
                return windowInstance

            # Set WindowID if needed but disable saving
            # TODO: Override output to match AbstractWindow.dialog
            # cmds.layoutDialog(dismiss=str(data)) to self.dialogAccept(data)
            class WindowClass(windowClass):
                if not hasattr(windowClass, 'WindowID'):
                    WindowID = uuid.uuid4().hex
                    def enableSaveWindowPosition(self, enable):
                        return super(WindowClass, self).enableSaveWindowPosition(False)

            try:
                return mc.layoutDialog(
                    ui=partial(uiScript, WindowClass, clsArgs=args, clsKwargs=kwargs),
                    title=getattr(cls, 'WindowTitle', 'New Window'),
                )
            finally:
                cls.clearWindowInstance(cls.WindowID)

        if parent is None:
            parent = getMainWindow()
        return super(MayaWindow, cls).dialog(parent=parent, *args, **kwargs)


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

    @classmethod
    def dialog(cls, parent=None, *args, **kwargs):
        """Create the window as a dialog."""
        if parent is None:
            parent = getMainWindow()
        return super(NukeWindow, cls).dialog(parent=parent, *args, **kwargs)
