from __future__ import absolute_import

from functools import partial

import maya.api.OpenMaya as om2
import maya.cmds as mc

from ..abstract.callbacks import AbstractCallbacks, CallbackProxy


class MayaCallbacks(AbstractCallbacks):
    def add(self, name, func, *args, **kwargs):
        """Register a callback.

        Implemented:
            'new' (same as 'new.after')
            'new.before'
            'new.before.check'
            'new.after'
            'open' (same as 'open.after')
            'open.before'
            'open.before.check'
            'open.after'
            'save' (same as 'save.after')
            'save.before'
            'save.before.check'
            'save.after'
            'import' (same as 'import.after')
            'import.before'
            'import.before.check'
            'import.after'
            'reference'  (same as 'reference.create.after')
            'reference.create'  (same as 'reference.create.after')
            'reference.create.before'
            'reference.create.before.check'
            'reference.create.after'
            'reference.remove'  (same as 'reference.remove.after')
            'reference.remove.before'
            'reference.remove.after'
            'reference.load'  (same as 'reference.load.after')
            'reference.load.before'
            'reference.load.before.check'
            'reference.load.after'
            'reference.unload'  (same as 'reference.unload.after')
            'reference.unload.before'
            'reference.unload.after'
            'reference.import'  (same as 'reference.import.after')
            'reference.import.before'
            'reference.import.after'
            'reference.export'  (same as 'reference.export.after')
            'reference.export.before'
            'reference.export.after'
            'render'  (same as 'render.software.after')
            'render.software'  (same as 'render.software.after')
            'render.software.before'
            'render.software.after'
            'render.software.frame'  (same as 'render.software.frame.after')
            'render.software.frame.before'
            'render.software.frame.after'
            'render.software.interrupted'
            'application.start'
            'application.exit'
            'plugin.load'  (same as 'plugin.load.after')
            'plugin.load.before'
            'plugin.load.after'
            'plugin.unload'  (same as 'plugin.unload.after')
            'plugin.unload.before'
            'plugin.unload.after'
            'connection'  (same as 'connection.after')
            'connection.before'
            'connection.changed'
            'node.added'
            'node.removed'
            'node.dirty'
            'node.dirty.plug'
            'node.name.changed'
            'node.uuid.changed'
            'frame.changed'
            'frame.changed.deferred'
            'attribute.changed'
            'attribute.value.changed'
            'attribute.keyable.changed'

        TODO:
            'scriptjob.event'
            'scriptjob.condition'

            om.MEventMessage.getEventNames():
                om.MEventMessage.addEventCallback
                om.MMessage.removeCallback
                undo
                redo
                timeChanged
                ActiveViewChanged
                cameraChange
                time.changed
                selection.changed
        """
        parts = name.split('.') + [None, None, None]

        sceneMessage = None
        sceneCheckMessage = None
        sceneFileCheckMessage = None
        sceneStringArrayMessage = None
        scriptJobEvent = None
        scriptJobCondition = None
        dgMessage = None
        nodeMessage = None

        if parts[0] == 'new':
            if parts[1] == 'before':
                if parts[2] == 'check':
                    sceneCheckMessage = om2.MSceneMessage.kBeforeNewCheck
                elif parts[2] is None:
                    sceneMessage = om2.MSceneMessage.kBeforeNew
            elif parts[1] in ('after', None):
                sceneMessage = om2.MSceneMessage.kAfterNew

        elif parts[0] == 'open':
            if parts[1] == 'before':
                if parts[2] == 'check':
                    sceneFileCheckMessage = om2.MSceneMessage.kBeforeOpenCheck
                elif parts[2] is None:
                    sceneMessage = om2.MSceneMessage.kBeforeOpen
            elif parts[1] in ('after', None):
                sceneMessage = om2.MSceneMessage.kAfterOpen

        elif parts[0] == 'save':
            if parts[1] == 'before':
                if parts[2] == 'check':
                    sceneCheckMessage = om2.MSceneMessage.kBeforeSaveCheck
                elif parts[2] is None:
                    sceneMessage = om2.MSceneMessage.kBeforeSave
            elif parts[1] in ('after', None):
                sceneMessage = om2.MSceneMessage.kAfterSave

        elif parts[0] == 'import':
            if parts[1] == 'before':
                if parts[2] == 'check':
                    sceneFileCheckMessage = om2.MSceneMessage.kBeforeImportCheck
                elif parts[2] is None:
                    sceneMessage = om2.MSceneMessage.kBeforeImport
            elif parts[1] in ('after', None):
                sceneMessage = om2.MSceneMessage.kAfterImport

        elif parts[0] == 'export':
            if parts[1] == 'before':
                if parts[2] == 'check':
                    sceneFileCheckMessage = om2.MSceneMessage.kBeforeExportCheck
                elif parts[2] is None:
                    sceneMessage = om2.MSceneMessage.kBeforeExport
            elif parts[1] in ('after', None):
                sceneMessage = om2.MSceneMessage.kAfterExport

        elif parts[0] == 'reference':
            if parts[1] in ('create', None):
                if parts[2] == 'before':
                    if parts[3] == 'check':
                        sceneFileCheckMessage = om2.MSceneMessage.kBeforeCreateReferenceCheck
                    elif parts[3] is None:
                        sceneMessage = om2.MSceneMessage.kBeforeCreateReference
                elif parts[2] in ('after', None):
                    sceneMessage = om2.MSceneMessage.kAfterCreateReference

            elif parts[1] == 'remove':
                if parts[2] == 'before':
                    sceneMessage = om2.MSceneMessage.kBeforeRemoveReference
                elif parts[2] in ('after', None):
                    sceneMessage = om2.MSceneMessage.kAfterRemoveReference

            elif parts[1] == 'load':
                if parts[2] == 'before':
                    if parts[3] == 'check':
                        sceneFileCheckMessage = om2.MSceneMessage.kBeforeLoadReferenceCheck
                    elif parts[3] is None:
                        sceneMessage = om2.MSceneMessage.kBeforeLoadReference
                elif parts[2] in ('after', None):
                    sceneMessage = om2.MSceneMessage.kAfterLoadReference

            elif parts[1] == 'unload':
                if parts[2] == 'before':
                    sceneMessage = om2.MSceneMessage.kBeforeUnloadReference
                elif parts[2] in ('after', None):
                    sceneMessage = om2.MSceneMessage.kAfterUnloadReference

            elif parts[1] == 'import':
                if parts[2] == 'before':
                    sceneMessage = om2.MSceneMessage.kBeforeImportReference
                elif parts[2] in ('after', None):
                    sceneMessage = om2.MSceneMessage.kAfterImportReference

            elif parts[1] == 'export':
                if parts[2] == 'before':
                    sceneMessage = om2.MSceneMessage.kBeforeExportReference
                elif parts[2] in ('after', None):
                    sceneMessage = om2.MSceneMessage.kAfterExportReference

        elif parts[0] == 'render':
            if parts[1] in ('software', None):
                if parts[2] == 'before':
                    sceneMessage = om2.MSceneMessage.kBeforeSoftwareRender
                elif parts[2] in ('after', None):
                    sceneMessage = om2.MSceneMessage.kAfterSoftwareRender
                elif parts[2] == 'frame':
                    if parts[3] == 'before':
                        sceneMessage = om2.MSceneMessage.kBeforeSoftwareFrameRender
                    elif parts[3] in ('after', None):
                        sceneMessage = om2.MSceneMessage.kAfterSoftwareFrameRender
                elif parts[2] == 'interrupted':
                    sceneMessage = om2.MSceneMessage.kSoftwareRenderInterrupted

        elif parts[0] == 'application':
            if parts[1] == 'start':
                sceneMessage = om2.MSceneMessage.kMayaInitialized
            elif parts[1] == 'end':
                sceneMessage = om2.MSceneMessage.kMayaExiting

        elif parts[0] == 'plugin':
            if parts[1] == 'load':
                if parts[2] == 'before':
                    sceneStringArrayMessage = om2.MSceneMessage.kBeforePluginLoad
                elif parts[2] in ('after', None):
                    sceneStringArrayMessage = om2.MSceneMessage.kAfterPluginLoad
            elif parts[1] == 'unload':
                if parts[2] == 'before':
                    sceneStringArrayMessage = om2.MSceneMessage.kBeforePluginUnload
                elif parts[2] in ('after', None):
                    sceneStringArrayMessage = om2.MSceneMessage.kAfterPluginUnload

        elif parts[0] == 'connection':
            if parts[1] == 'before':
                dgMessage = om2.MDGMessage.addPreConnectionCallback
            elif parts[2] in ('after', None):
                dgMessage = om2.MDGMessage.addConnectionCallback

        elif parts[0] == 'node':
            if parts[1] == 'added':
                dgMessage = om2.MDGMessage.addNodeAddedCallback
            elif parts[1] == 'removed':
                # if parts[2] == 'before':
                #     nodeMessage = om2.MNodeMessage.addNodePreRemovalCallback
                # elif parts[2] in ('after', None):
                #     dgMessage = om2.MDGMessage.addNodeRemovedCallback
                dgMessage = om2.MDGMessage.addNodeRemovedCallback
            elif parts[1] == 'name':
                if parts[2] == 'changed':
                    nodeMessage = om2.MNodeMessage.addNameChangedCallback
            elif parts[1] == 'uuid':
                if parts[2] == 'changed':
                    nodeMessage = om2.MNodeMessage.addUUIdChangedCallback
            elif parts[2] == 'dirty':
                if parts[3] == 'plug':
                    nodeMessage = om2.MNodeMessage.addNodeDirtyPlugCallback
                elif parts[3] is None:
                    nodeMessage = om2.MNodeMessage.addNodeDirtyCallback
            elif parts[2] == 'destroyed':
                nodeMessage = om2.MNodeMessage.addNodeDestroyedCallback

        elif parts[0] == 'frame':
            if parts[1] == 'changed':
                if parts[2] is None:
                    dgMessage = om2.MDGMessage.addTimeChangeCallback
                elif parts[2] == 'deferred':
                    dgMessage = om2.MDGMessage.addForceUpdateCallback

        elif parts[0] == 'attribute':
            if parts[1] == 'changed':
                nodeMessage = om2.MNodeMessage.addAttributeAddedOrRemovedCallback
            elif parts[1] == 'value':
                if parts[2] == 'changed':
                    nodeMessage = om2.MNodeMessage.addAttributeChangedCallback
            elif parts[1] == 'keyable':
                if parts[2] == 'changed':
                    nodeMessage = om2.MNodeMessage.addKeyableChangeOverride

        if sceneMessage is not None:
            register = partial(om2.MSceneMessage.addCallback, sceneMessage)
            unregister = om2.MSceneMessage.removeCallback
        elif sceneCheckMessage is not None:
            register = partial(om2.MSceneMessage.addCheckCallback, sceneCheckMessage)
            unregister = om2.MSceneMessage.removeCallback
        elif sceneFileCheckMessage is not None:
            register = partial(om2.MSceneMessage.addCheckFileCallback, sceneFileCheckMessage)
            unregister = om2.MSceneMessage.removeCallback
        elif sceneStringArrayMessage is not None:
            register = partial(om2.MSceneMessage.addStringArrayCallback, sceneStringArrayMessage)
            unregister = om2.MSceneMessage.removeCallback
        elif dgMessage is not None:
            register = dgMessage
            unregister = om2.MMessage.removeCallback
        elif nodeMessage is not None:
            register = nodeMessage
            unregister = om2.MNodeMessage.removeCallback
        elif scriptJobEvent is not None:
            register = lambda func, *args, **kwargs: mc.scriptJob(event=[scriptJobEvent, func], *args, **kwargs)
            unregister = lambda callbackID: mc.scriptJob(kill=callbackID)
        elif scriptJobCondition is not None:
            register = lambda func, *args, **kwargs: mc.scriptJob(conditionChange=[scriptJobCondition, func], *args, **kwargs)
            unregister = lambda callbackID: mc.scriptJob(kill=callbackID)
        else:
            return None

        callback = CallbackProxy(name, register, unregister, func, args, kwargs).register()
        self._callbacks.append(callback)
        return callback

    def registerScene(self, msg, func, clientData=None):
        """Register an MSceneMessage callback."""
        callbackID = om2.MSceneMessage.addCallback(msg, func, clientData)

    def registerSceneCheck(self, msg, func, clientData=None):
        """Register a scene check callback.
        Returning False will abort the current operation.

        Example:
            >>> def beforeSave(clientData=None):
            ...     return askUser()
            >>> msg = om2.MSceneMessage.kBeforeSaveCheck
            >>> self.registerSceneCheckCallback(msg, beforeSave)

        Messages:
            kBeforeNewCheck
            kBeforeImportCheck
            kBeforeOpenCheck
            kBeforeExportCheck
            kBeforeSaveCheck
            kBeforeCreateReferenceCheck
            kBeforeLoadReferenceCheck
        """
        addCheckCallback

    def registerSceneFileCheck(self, msg, func, clientData=None, group=None):
        """Register a scene check callback that takes an MFileObject argument.
        By modifying the MFileObject the target file will be changed as well.
        Returning False will abort the current operation.

        Example:
            >>> def beforeOpen(file, clientData=None):
            ...     if fileObj.resolvedFullName().startswith('F:'):
            ...         mc.warning('Not allowed to open scenes on F drive')
            ...         return False
            ...     return True
            >>> msg = om2.MSceneMessage.kBeforeOpenCheck
            >>> self.registerSceneFileCheckCallback(msg, beforeOpen)

        Messages:
            kBeforeImportCheck
            kBeforeOpenCheck
            kBeforeExportCheck
            kBeforeCreateReferenceCheck
            kBeforeLoadReferenceCheck
        """
        addCheckFileCallback

    def registerSceneStringArray(self, msg, func, clientData=None, group=None):
        """Register a callback that takes a string array argument.
        In the future more array elements may be added, so callbacks
        should not rely on a fixed length.

        Example:
        >>> def afterPluginLoad(stringArray, clientData=None):
        ...     path, name = stringArray[:2]
        ...     print(f'Loaded {name} from {path}')

        Messages:
            kBeforePluginLoad (path)
            kAfterPluginLoad (path, name)
            kBeforePluginUnload (name)
            kAfterPluginUnload (name, path)
        """
        addStringArrayCallback

    def registerScriptJobEvent(self, msg, func, group=None, runOnce=False):
        mc.scriptJob(runOnce=runOnce, event=[msg, func])

    def registerScriptJobCondition(self, msg, func, group=None, runOnce=False):
        mc.scriptJob(runOnce=runOnce, conditionChange=[msg, func])

    def registerTimeChange(self, func, group=None):
        om2.MDGMessage.addTimeChangeCallback

    def registerForceUpdate(self, func, group=None):
        om2.MDGMessage.addForceUpdateCallback

    def registerNodeAdded(self, func, nodeType='dependNode', clientData=None):
        om2.MDGMessage.addNodeAddedCallback

    def registerNodeRemoved(self, func, nodeType='dependNode', clientData=None):
        """Run a callback when a node is removed.

        Parameters:
            func: The callback function.
            nodeType: Type of node to trigger the callback.
                The default is "dependNode" which matches all node.

        Callback Parameters:
            node: The node being removed.
            clientData: User defined data.
        """

        om2.MDGMessage.addNodeRemovedCallback

    def registerConnection(self, func, group=None):
        """Run a callback after a connection is made or broken.

        Callback Parameters:
            srcPlug: Source plug of the connection.
            destPlug: Destination plug of the connection.
            made: If a connection was made or broken.
            clientData: User defined data.
        """
        om2.MDGMessage.addConnectionCallback

    def registerPreConnection(self, func, group=None):
        """Run a callback before a connection is made or broken.

        Callback Parameters:
            srcPlug: Source plug of the connection.
            destPlug: Destination plug of the connection.
            made: If a connection was made or broken.
            clientData: User defined data.
        """
        om2.MDGMessage.addPreConnectionCallback

    def registerNodeMessage(self, msg):
        """

        Messages:
        The type of attribute changed/addedOrRemoved messages that has occurred.

            kConnectionMade: a connection has been made to an attribute of this node
            kConnectionBroken: a connection has been broken for an attribute of this node
            kAttributeEval: an attribute of this node has been evaluated
            kAttributeSet: an attribute value of this node has been set
            kAttributeLocked: an attribute of this node has been locked
            kAttributeUnlocked: an attribute of this node has been unlocked
            kAttributeAdded: an attribute has been added to this node
            kAttributeRemoved: an attribute has been removed from this node
            kAttributeRenamed: an attribute of this node has been renamed
            kAttributeKeyable: an attribute of this node has been marked keyable
            kAttributeUnkeyable: an attribute of this node has been marked unkeyable
            kIncomingDirection: connection was coming into the node
            kAttributeArrayAdded: an array attribute has been added to this node
            kAttributeArrayRemoved: an array attribute has been removed from this node
            kOtherPlugSet: the otherPlug data has been set
        """
