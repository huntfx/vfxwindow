"""Window class for Maya."""

from __future__ import absolute_import, print_function

import uuid
from functools import partial

import maya.mel as mel
import maya.api.OpenMaya as om
import maya.OpenMayaUI as omUI
import pymel.core as pm
from pymel import versions

from .base import BaseWindow, getWindowSettings
from .utils import hybridmethod, setCoordinatesToScreen
from .utils.Qt import QtWidgets, QtCompat, QtCore


MAYA_VERSION = int(versions.flavor())


def getMayaWindow(windowID=None, wrapInstance=True):
    """Get pointer to main Maya window.
    The pointer type is a QWidget, so wrap to that (though it can be wrapped to other things too).
    """
    if wrapInstance:
        if windowID is not None:
            # ID is possibly a Maya widget
            if '|' in str(windowID):
                qtObj = pm.uitypes.toQtObject(windowID)
                if qtObj is not None:
                    return qtObj
            
            # ID is an existing window
            pointer = omUI.MQtUtil.findControl(windowID)
        else:
            pointer = omUI.MQtUtil.mainWindow()
        if pointer is not None:
            return QtCompat.wrapInstance(int(pointer), QtWidgets.QWidget)

    # Fallback to searching widgets
    if isinstance(windowID, QtWidgets.QWidget):
        return obj
    search = windowID or 'MayaWindow'
    for obj in QtWidgets.QApplication.topLevelWidgets():
        if obj.objectName() == search:
            return obj


def deleteWorkspaceControl(windowID, resetFloating=True):
    """Handle deleting a workspaceControl with a particular ID."""
    exists = pm.workspaceControlState(windowID, query=True, exists=True)
    try:
        floating = pm.workspaceControl(windowID, query=True, floating=True)
        pm.deleteUI(windowID)
        #pm.workspaceControl(id, edit=True, close=True) #appears to do the same thing so diabled
    except RuntimeError:
        floating = None
    else:
        #Do not reset workspace if the window is currently floating
        if not resetFloating:
            exists = not floating

    #Delete the window preferences (position, size, etc)
    if exists:
        pm.workspaceControlState(windowID, remove=True)

    return floating


def deleteDockControl(windowID):
    """Handle deleting a dockControl with a particular ID."""
    # Get current floating state
    if pm.dockControl(windowID, query=True, exists=True):
        floating = pm.dockControl(windowID, query=True, floating=True)
        pm.dockControl(windowID, edit=True, r=True)
        pm.dockControl(windowID, edit=True, floating=False)
    else:
        floating = None

    # Close down the dock control
    windowWrap = getMayaWindow(windowID)
    if windowWrap is not None:
        if windowWrap.parent().parent() is not None:
            getMayaWindow(windowID).parent().close()
    
    if floating is not None:
        try:
            pm.dockControl(windowID, edit=True, floating=floating)
        except RuntimeError:
            pass

    return floating


def workspaceControlWrap(windowClass, dock=True, resetFloating=True, *args, **kwargs):
    """Template class for docking a Qt widget to maya 2017+.
    Requires the window to contain the attributes ID and NAME.

    Source (heavily modified): https://gist.github.com/liorbenhorin/69da10ec6f22c6d7b92deefdb4a4f475
    """
    # Set window ID if needed but disable saving
    if not hasattr(windowClass, 'ID'):
        windowClass.ID = str(uuid.uuid4())
        windowClass.saveWindowPosition = lambda *args, **kwargs: None

    # Remove existing window
    floating = deleteWorkspaceControl(windowClass.ID, resetFloating=resetFloating)
    if not resetFloating and floating is None:
        floating = not dock

    # Setup Maya's window
    if dock:
        if isinstance(dock, (bool, int)):
            dock = 'AttributeEditor'
        pm.workspaceControl(windowClass.ID, retain=True, label=getattr(windowClass, 'NAME', 'New Window'), tabToControl=[dock, -1])
    else:
        pm.workspaceControl(windowClass.ID, retain=True, label=getattr(windowClass, 'NAME', 'New Window'), floating=True)

    # Setup main window and parent to Maya
    workspaceControlWin = getMayaWindow(windowClass.ID)
    workspaceControlWin.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    windowInstance = windowClass(parent=workspaceControlWin, dockable=True, *args, **kwargs)

    # Attach callbacks
    windowInstance.signalConnect(workspaceControlWin.destroyed, windowInstance.close, group='__mayaDockWinDestroy')
    try:
        pm.workspaceControl(windowClass.ID, edit=True, visibleChangeCommand=windowInstance.visibleChangeEvent)
    except (AttributeError, TypeError):
        pass
    try:
        windowInstance.loadWindowPosition()
    except (AttributeError, TypeError):
        pass
    
    # Restore the window (after maya is ready) since it may not be visible
    windowInstance.deferred(windowInstance.raise_)
    windowInstance.deferred(windowInstance.windowReady.emit)
    return windowInstance


def dockControlWrap(windowClass, dock=True, resetFloating=True, *args, **kwargs):
    
    def attachToDockControl(windowInstance, floating=False, area='right'):
        """This needs to be deferred as it can run before the previous dockControl has closed."""

        controlName = pm.dockControl(windowInstance.ID, area=area, floating=False, retain=False, content=windowInstance.objectName(), closeCommand=windowInstance.close)

        windowInstance.setDocked(not floating)
        try:
            pm.dockControl(windowInstance.ID, edit=True, floatChangeCommand=windowInstance.saveWindowPosition)
        except (AttributeError, TypeError):
            pass

        try:
            windowInstance.deferred(windowInstance.loadWindowPosition)
        except (AttributeError, TypeError):
            pass

        windowInstance.setWindowTitle(getattr(windowInstance, 'NAME', 'New Window'))
        windowInstance.deferred(windowInstance.raise_)
        windowInstance.deferred(windowInstance.windowReady.emit)
        
    # Set window ID if needed but disable saving
    if not hasattr(windowClass, 'ID'):
        windowClass.ID = str(uuid.uuid4())
        windowClass.saveWindowPosition = lambda *args, **kwargs: None
    
    # Remove existing window
    floating = deleteDockControl(windowClass.ID)
    if not resetFloating or floating is None:
        floating = not dock

    # Setup main window and parent to Maya
    mayaWin = getMayaWindow(wrapInstance=False)
    windowInstance = windowClass(parent=mayaWin, dockable=True, *args, **kwargs)
    windowInstance.deferred(attachToDockControl, windowInstance, floating)

    # Restore the window (after maya is ready) since it may not be visible
    return windowInstance


def dialogWrapper(windowClass, title=None, clsArgs=(), clsKwargs={}):
    """Wrapper for Maya's layoutDialogue class.
    It will take focus of the entire program.

    Note: Due to Python 2 limitations, *args and **kwargs can't be unpacked with the title keyword
    present, so don't try to clean up the code by enabling unpacking again.
    """
    def uiScript(cls, clsArgs=(), clsKwargs={}):
        form = pm.setParent(query=True)
        parent = pm.uitypes.toQtObject(form)
        parent.layout().setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

        windowInstance = cls(parent, *clsArgs, **clsKwargs)
        windowInstance.windowReady.emit()
        return windowInstance
    return pm.layoutDialog(ui=partial(uiScript, windowClass, clsArgs=clsArgs, clsKwargs=clsKwargs), title=title)


def toMObject(node):
    """Convert a node to an MObject."""
    if isinstance(node, om.MObject):
        return node
    selected = om.MSelectionList()
    selected.add(str(node))
    return selected.getDependNode(0)


class MayaWindow(BaseWindow):
    """Inhert from this for dockable Maya windows.

    This is an alternative to maya.app.general.mayaMixin.MayaQWidgetDockableMixin, as many features
    were already implemented when I found it. It is missing a few parts I would have liked though.
    """

    def __init__(self, parent=None, dockable=False, **kwargs):
        if parent is None:
            parent = getMayaWindow()
        super(MayaWindow, self).__init__(parent, **kwargs)
        self.maya = True
        self.setDockable(dockable, override=True)

        # The line below can save the window preferences, but this window automatically does it
        #self.setProperty("saveWindowPref", True)

        self.__parentTemp = None

    def visibleChangeEvent(self, *args, **kwargs):
        """This probably means the window has just been closed."""
        if self.dockable():
            self.saveWindowPosition()

    def closeEvent(self, event):
        """Handle the class being deleted."""
        dockable = self.dockable()
        if not dockable:
            self.saveWindowPosition()
        elif MAYA_VERSION < 2017:
            try:
                self.saveWindowPosition()
            except TypeError:
                pass
        self.clearWindowInstance(self.ID, deleteWindow=True)

        # If dockControl is being used, then Maya will crash if close is called
        if dockable and MAYA_VERSION < 2017:
            event.ignore()
        else:
            return super(MayaWindow, self).closeEvent(event)

    def exists(self):
        if self.dockable():
            if MAYA_VERSION < 2017:
                return pm.dockControl(self.ID, query=True, exists=True)
            return pm.workspaceControl(self.ID, query=True, exists=True)
        return not self.isClosed()

    def raise_(self):
        if self.dockable():
            if MAYA_VERSION < 2017:
                return pm.dockControl(self.ID, edit=True, r=True)
            return pm.workspaceControl(self.ID, edit=True, restore=True)
        return super(MayaWindow, self).raise_()

    def setWindowTitle(self, title):
        if self.dockable():
            try:
                if MAYA_VERSION < 2017:
                    return pm.dockControl(self.ID, edit=True, label=title)
                return pm.workspaceControl(self.ID, edit=True, label=title)
            except RuntimeError:
                pass
        return super(MayaWindow, self).setWindowTitle(title)

    def isVisible(self):
        if self.dockable():
            try:
                if MAYA_VERSION < 2017:
                    return pm.dockControl(self.ID, query=True, visible=True)
                return pm.workspaceControl(self.ID, query=True, visible=True)
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
            if MAYA_VERSION < 2017:
                self.raise_()
                pm.dockControl(self.ID, edit=True, floating=not dock)
                self.raise_()
            else:
                pm.workspaceControl(self.ID, edit=True, floating=not dock)

    def windowPalette(self):
        currentPalette = super(MayaWindow, self).windowPalette()
        if currentPalette is None:
            return 'Maya.{}'.format(MAYA_VERSION)
        return currentPalette

    def _parentOverride(self, create=True):
        """Get the correct parent needed to query window data.
        It needs to be set to an attribute or Python will forget the C++ pointer.
        """
        if MAYA_VERSION < 2017:
            return self.parent()

        #Determine if it's a new window, we need to get the C++ pointer again
        if self.__parentTemp is None:
            base = getMayaWindow(self.ID)
        else:
            base = self.parent()

        #Get the correct parent level
        if self.floating():
            self.__parentTemp = base.parent().parent().parent().parent()
        else:
            self.__parentTemp = base.parent().parent()
        return self.__parentTemp

    def floating(self):
        if MAYA_VERSION < 2017:
            return pm.dockControl(self.ID, query=True, floating=True)
        return pm.workspaceControl(self.ID, query=True, floating=True)
        
    def resize(self, width, height):
        """Resize the window."""
        if self.dockable():
            if MAYA_VERSION < 2017:
                if not self.floating():
                    return pm.dockControl(self.ID, edit=True, width=width, height=height)
            else:
                return pm.workspaceControl(self.ID, edit=True, resizeWidth=width, resizeHeight=height)
        return super(MayaWindow, self).resize(width, height)

    def siblings(self):
        if self.dockable():
            if MAYA_VERSION < 2017:
                return []
            return self.parent().parent().children()
        return []

    def control(self):
        """Return the Maya Control name, so it can be attached again."""
        if not self.dockable():
            return None
        
        # Pre-2017 only has 'top', 'bottom', 'left' and 'right'
        if MAYA_VERSION < 2017:
            return pm.dockControl(self.ID, query=True, area=True)
        
        # Search through siblings until a 
        parent = self.parent()
        for item in self.siblings():
            if item != parent and type(item) == QtWidgets.QWidget:
                try:
                    return item.objectName()
                except RuntimeError:
                    pass

        # Verbose way
        # TODO: Needs testing if this is still needed
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
            widget = pm.uitypes.toQtControl(control)
            if widget is not None:
                if widget.parent() is stackedWidget:
                    return control
        return None

    def centreWindow(self):
        """Centre the window using geometry of the main Maya window."""
        if self.dockable():
            try:
                parentGeometry = self._parentOverride().parent().frameGeometry()
            except RuntimeError:
                return None
        else:
            parentGeometry = self.parent().frameGeometry()
        return super(MayaWindow, self).centreWindow(parentGeometry=parentGeometry)
    
    def saveWindowPosition(self):
        """Save the window location."""
        try:
            mayaSettings = self.windowSettings['maya']
        except KeyError:
            mayaSettings = self.windowSettings['maya'] = {}
        mayaSettings['docked'] = self.dockable(raw=True)
        try:
            if self.dockable():
                try:
                    dockWindowSettings = mayaSettings['dock']
                except KeyError:
                    dockWindowSettings = mayaSettings['dock'] = {}
                dockWindowSettings['width'] = self.width()
                dockWindowSettings['height'] = self.height()
                dockWindowSettings['x'] = self.x()
                dockWindowSettings['y'] = self.y()
                dockWindowSettings['floating'] = self.floating()
                dockWindowSettings['control'] = self.control()
            else:
                try:
                    mainWindowSettings = mayaSettings['main']
                except KeyError:
                    mainWindowSettings = mayaSettings['main'] = {}
                mainWindowSettings['width'] = self.width()
                mainWindowSettings['height'] = self.height()
                mainWindowSettings['x'] = self.x()
                mainWindowSettings['y'] = self.y()
        except RuntimeError:
            if not self.dockable():
                raise
        else:
            super(MayaWindow, self).saveWindowPosition()
        
    def loadWindowPosition(self):
        """Set the position of the window when loaded."""
        try:
            if self.dockable():
                settings = self.windowSettings['maya']['dock']
                control = settings['control']
            else:
                settings = self.windowSettings['maya']['main']
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
            if self.dockable() and MAYA_VERSION < 2017:
                pm.dockControl(self.ID, edit=True, area=control)

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
            groups = windowInstance['callback'].keys()
        else:
            if group not in windowInstance['callback']:
                return 0
            groups = [group]
        
        # Iterate through each callback to remove certain groups
        num_events = 0
        for group in groups:
            for callback_id in windowInstance['callback'][group]['event']:
                try:
                    om.MMessage.removeCallback(callback_id)
                except RuntimeError:
                    pass
                else:
                    num_events += 1
            for callback_id in windowInstance['callback'][group]['node']:
                try:
                    om.MNodeMessage.removeCallback(callback_id)
                except RuntimeError:
                    pass
                else:
                    num_events += 1
            for callback_id in windowInstance['callback'][group]['scene']:
                try:
                    om.MSceneMessage.removeCallback(callback_id)
                except RuntimeError:
                    pass
                else:
                    num_events += 1
            for callback_id in windowInstance['callback'][group]['job']:
                try:
                    pm.scriptJob(kill=callback_id)
                except RuntimeError:
                    pass
                else:
                    num_events += 1
            del windowInstance['callback'][group]
        return num_events

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

    def addCallbackEvent(self, callback, func, clientData=None, group=None):
        """Add an event callback.

        Parameters:
            callback (str)
            func
            clientData
            group

        Returns:
            clientData

        Notable Callbacks:
            timeChanged
            SelectionChanged
            Undo / Redo

        All Callbacks: om.MEventMessage.getEventNames()
        """
        self._addMayaCallbackGroup(group)
        self.windowInstance()['callback'][group]['event'].append(om.MEventMessage.addEventCallback(callback, func, clientData))

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

        All Callbacks/Attributes: https://help.autodesk.com/view/MAYAUL/2016/ENU/?guid=__py_ref_class_open_maya_1_1_m_node_message_html

        Example:
            def callback(msg, plug, otherPlug, *args):
                if msg & om.MNodeMessage.kAttributeLocked:
                    print 'Attribute {} was locked.'.format(plug1.name())
                if msg & om.MNodeMessage.kAttributeUnlocked:
                    print 'Attribute {} was unlocked.'.format(plug1.name())
            callbackID = addNodeCallback('pCubeShape1')
            om.MNodeMessage.removeCallback(callbackID)
        """
        self._addMayaCallbackGroup(group)
        self.windowInstance()['callback'][group]['node'].append(callback(toMObject(node), func, clientData))

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
        self.addCallbackNode(om.MNodeMessage.addAttributeChangedCallback, node, func, clientData, group=group)

    def addCallbackAttributeAddOrRemove(self, node, func, clientData=None, group=None):
        """Add an MNodeMessage callback for when an attribute is added.
        
        Official Documentation:
            This is a more specific version of addAttributeChanged as only attribute
            added and attribute removed messages will trigger the callback.
        See MayaWindow.addCallbackNode for details.
        """
        self.addCallbackNode(om.MNodeMessage.addAttributeAddedOrRemovedCallback, node, func, clientData, group=group)

    def addCallbackNodeRename(self, node, func, clientData=None, group=None):
        """Add an MNodeMessage callback for when a node is renamed.

        See MayaWindow.addCallbackNode for details.
        """
        self.addCallbackNode(om.MNodeMessage.addNameChangedCallback, node, func, clientData, group=group)

    def addCallbackNodeDirty(self, node, func, clientData=None, group=None):
        """Add an MNodeMessage callback for node dirty messages.

        See MayaWindow.addCallbackNode for details.
        """
        self.addCallbackNode(om.MNodeMessage.addNodeDirtyCallback, node, func, clientData, group=group)

    def addCallbackNodeDirtyPlug(self, node, func, clientData=None, group=None):
        """Add an MNodeMessage callback for node dirty messages.

        Official Documentation:
            This callback provides the plug on the node that was dirtied.
            Only provides dirty information on input plugs.
        See MayaWindow.addCallbackNode for details.
        """
        self.addCallbackNode(om.MNodeMessage.addNodeDirtyPlugCallback, node, func, clientData, group=group)

    def addCallbackUuidChange(self, node, func, clientData=None, group=None):
        """Add an MNodeMessage callback for when a node UUID is changed.

        See MayaWindow.addCallbackNode for details.
        """
        self.addCallbackNode(om.MNodeMessage.addUuidChangedCallback, node, func, clientData, group=group)

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
        self.addCallbackNode(om.MNodeMessage.addKeyableChangeOverride, node, func, clientData, group=group)

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
        self.addCallbackNode(om.MNodeMessage.addNodePreRemovalCallback, node, func, clientData, group=group)

    def addCallbackScene(self, callback, func, clientData=None, group=None):
        """Add a scene callback.

        Returns:
            clientData

        Notable Callbacks:
            kBeforeNew / kAfterNew
            kBeforeOpen / kAfterOpen
            kBeforeSave / kAfterSave

        All Callbacks: http://download.autodesk.com/us/maya/2011help/api/class_m_scene_message.html
        """
        self._addMayaCallbackGroup(group)
        if not isinstance(callback, int):
            callback = getattr(om.MSceneMessage, callback)
        self.windowInstance()['callback'][group]['scene'].append(om.MSceneMessage.addCallback(callback, func, clientData))

    def addCallbackJobEvent(self, callback, func, group=None, runOnce=False):
        self._addMayaCallbackGroup(group)
        self.windowInstance()['callback'][group]['job'].append(pm.scriptJob(runOnce=runOnce, event=[callback, func]))

    def addCallbackJobCondition(self, callback, func, group=None, runOnce=False):
        self._addMayaCallbackGroup(group)
        self.windowInstance()['callback'][group]['job'].append(pm.scriptJob(runOnce=runOnce, conditionChange=[callback, func]))

    def addCallbackNodeTypeAdd(self, func, nodeType='dependNode', clientData=None, group=None):
        """Add an MDGMessage callback for whenever a new node is added to the dependency graph."""
        self._addMayaCallbackGroup(group)
        self.windowInstance()['callback'][group]['event'].append(om.MDGMessage.addNodeAddedCallback(func, nodeType, clientData))

    def addCallbackNodeTypeRemove(self, func, nodeType='dependNode', clientData=None, group=None):
        """Add an MDGMessage callback for whenever a new node is removed from the dependency graph.
        This is used instead of addNodeDestroyedCallback since nodes are not instantly destroyed.
        """
        self._addMayaCallbackGroup(group)
        self.windowInstance()['callback'][group]['event'].append(om.MDGMessage.addNodeRemovedCallback(func, nodeType, clientData))

    def addCallbackTimeChange(self, func, clientData=None, group=None):
        """Add an MDGMessage callback for whenever the time changes in the dependency graph."""
        self._addMayaCallbackGroup(group)
        self.windowInstance()['callback'][group]['event'].append(om.MDGMessage.addTimeChangeCallback(func, clientData))

    def addCallbackForceUpdate(self, func, clientData=None, group=None):
        """Add an MDGMessage callback for after the time changes and after all nodes have been evaluated in the dependency graph."""
        self._addMayaCallbackGroup(group)
        self.windowInstance()['callback'][group]['event'].append(om.MDGMessage.addForceUpdateCallback(func, clientData))

    def addCallbackConnectionAfter(self, func, clientData=None, group=None):
        """Add an MDGMessage callback for after a connection is made or broken in the dependency graph."""
        self._addMayaCallbackGroup(group)
        self.windowInstance()['callback'][group]['event'].append(om.MDGMessage.addConnectionCallback(func, clientData))

    def addCallbackConnectionBefore(self, func, clientData=None, group=None):
        """Add an MDGMessage callback for before a connection is made or broken in the dependency graph."""
        self._addMayaCallbackGroup(group)
        self.windowInstance()['callback'][group]['event'].append(om.MDGMessage.addPreConnectionCallback(func, clientData)(func, clientData))

    @classmethod
    def clearWindowInstance(self, windowID, deleteWindow=True):
        """Close the last class instance."""
        previousInstance = super(MayaWindow, self).clearWindowInstance(windowID)
        if previousInstance is None:
            return
        self.removeCallbacks(windowInstance=previousInstance)

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
            if MAYA_VERSION < 2017:
                deleteDockControl(previousInstance['window'].ID)
            else:
                deleteWorkspaceControl(previousInstance['window'].ID)
        return previousInstance

    def hide(self):
        """Hide the window."""
        if self.dockable():
            if MAYA_VERSION < 2017:
                return pm.dockControl(self.ID, edit=True, visible=False)
            return pm.workspaceControl(self.ID, edit=True, visible=False)
        return super(MayaWindow, self).hide()

    def setFocus(self):
        """Force Maya to focus on the window."""
        if self.dockable():
            return pm.setFocus(self.ID)
        return super(MayaWindow, self).setFocus()

    def deferred(self, func, *args, **kwargs):
        """Execute a deferred command.
        If the window is a dialog, then execute now as Maya will pause.
        """
        if getattr(self, 'DIALOG', False):
            func()
        else:
            pm.evalDeferred(func, *args, **kwargs)

    @hybridmethod
    def show(cls, self, *args, **kwargs):
        """Show the window.
        It can be as a docked or floating workspaceControl, or just a normal Qt window.

        If the window is just hidden, this should bring back into focus.
        Not tested yet however.
        """
        if self is not cls:
            # Case where window is already initialised
            if self.dockable():
                if MAYA_VERSION < 2017:
                    return pm.dockControl(self.ID, edit=True, visible=True)
                return pm.workspaceControl(self.ID, edit=True, visible=True)
            return super(MayaWindow, self).show()

        # Close down any instances of the window
        # If a dialog was opened, then the reference will no longer exist
        try:
            cls.clearWindowInstance(cls.ID, deleteWindow=False)
        except AttributeError:
            settings = {}
        else:
            settings = getWindowSettings(cls.ID)
        
        # Open a dialog window that will force control
        if MAYA_VERSION >= 2017 and getattr(cls, 'DIALOG', False):
            cls.DOCKABLE = False
            try:
                return dialogWrapper(
                    cls,
                    title=getattr(cls, 'NAME', 'New Window'),
                    clsArgs=args,
                    clsKwargs=kwargs
                )
            finally:
                cls.clearWindowInstance(cls.ID, deleteWindow=False)

        # Load settings
        try:
            mayaSettings = settings['maya']
        except KeyError:
            mayaSettings = settings['maya'] = {}

        if hasattr(cls, 'DOCKABLE'):
            docked = cls.DOCKABLE
        else:
            try:
                docked = settings['maya']['docked']
            except KeyError:
                try:
                    docked = cls.DEFAULTS['docked']
                except (AttributeError, KeyError):
                    docked = True

        # Return new class instance and show window
        if docked:
            if hasattr(cls, 'FLOATING'):
                floating = cls.FLOATING
            else:
                try:
                    floating = settings['maya']['dock']['floating']
                except KeyError:
                    try:
                        floating = cls.DEFAULTS['floating']
                    except (AttributeError, KeyError):
                        floating = False
            if floating:
                dock = False
            else:
                try:
                    dock = settings['maya']['dock'].get('control', True)
                except KeyError:
                    dock = True
            if MAYA_VERSION < 2017:
                return dockControlWrap(cls, dock, resetFloating=True, *args, **kwargs)
            return workspaceControlWrap(cls, dock, resetFloating=True, *args, **kwargs)

        return super(MayaWindow, cls).show(*args, **kwargs)
        