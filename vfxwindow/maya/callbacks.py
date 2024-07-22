from __future__ import absolute_import

from functools import partial

import maya.api.OpenMaya as om2
import maya.cmds as mc

from ..abstract.callbacks import AbstractCallbacks, CallbackProxy


class MayaCallbacks(AbstractCallbacks):
    def add(self, name, func, *args, **kwargs):
        """Register a callback.

        Callbacks:
            new:
                Mapped to 'new.after'.

            new.before:
                Called before a File > New operation.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            new.before.check:
                Called prior to File > New operation, allows user to cancel action.
                Parameters: (clientData=None)
                Signature: (clientData) -> bool

            new.after:
                Called after a File > New operation.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            open:
                Mapped to 'open.after'.

            open.before:
                Called before a File > Open operation.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            open.before.check:
                Called prior to File > Open operation, allows user to cancel action.
                Parameters: (clientData=None)
                Signature: (clientData) -> bool

            open.after:
                Called after a File > Open operation.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            save:
                Mapped to 'save.after'.

            save.before:
                Called before a File > Save (or SaveAs) operation.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            save.before.check:
                Called before a File > Save (or SaveAs) operation.
                Parameters: (clientData=None)
                Signature: (file: MFileObject, clientData) -> bool

            save.after:
                Called after a File > Save (or SaveAs) operation.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            import:
                Mapped to 'import.after'.

            import.before:
                Called before a File > Import operation.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            import.before.check:
                Called prior to File > Import operation, allows user to cancel action.
                Parameters: (clientData=None)
                Signature: (file: MFileObject, clientData) -> bool

            import.after:
                Called after a File > Import operation.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            export:
                Mapped to 'export.after'.

            export.before:
                Called before a File > Export operation.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            export.before.check:
                Called prior to File > Export operation, allows user to cancel action.
                Parameters: (clientData=None)
                Signature: (file: MFileObject, clientData) -> bool

            export.after:
                Called after a File > Export operation.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            reference:
                Mapped to 'reference.create.after'.

            reference.create:
                Mapped to 'reference.create.after'.

            reference.create.before:
                Called before a File > CreateReference operation.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            reference.create.before.check:
                Called prior to a File > CreateReference operation, allows user to cancel action.
                Parameters: (clientData=None)
                Signature: (file: MFileObject, clientData) -> bool

            reference.create.after
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            reference.remove:
                Mapped to 'reference.remove.after'.

            reference.remove.before:
                Called before a File > RemoveReference operation.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            reference.remove.after:
                Called after a File > RemoveReference operation.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            reference.load:
                Mapped to 'reference.load.after'.

            reference.load.before:
                Called before a File > LoadReference operation.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            reference.load.before.check:
                Called before a File > LoadReference operation, allows user to cancel action.
                Parameters: (clientData=None)
                Signature: (file: MFileObject, clientData) -> bool

            reference.load.after:
                Called after a File > LoadReference operation.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            reference.unload:
                Mapped to 'reference.unload.after'.

            reference.unload.before:
                Called before a File > UnloadReference operation.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            reference.unload.after:
                Called after a File > UnloadReference operation.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            reference.import:
                Mapped to 'reference.import.after'.

            reference.import.before':
                Called before a File > ImportReference operation.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            reference.import.after':
                Called after a File > ImportReference operation.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            reference.export':
                Mapped to 'reference.export.after')

            reference.export.before:
                Called before a File > ExportReference operation.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            reference.export.after:
                Called after a File > ExportReference operation.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            render:
                Mapped to 'render.software.after'

            render.software:
                Mapped to 'render.software.after'

            render.software.before:
                Called before a Software Render begins.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            render.software.after:
                Called after a Software Render ends.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            render.software.frame:
                Mapped to 'render.software.frame.after'
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            render.software.frame.before:
                Called before each frame of a Software Render.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            render.software.frame.after:
                Called after each frame of a Software Render.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            render.software.interrupted:
                Called when an interactive render is interrupted by the user.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            application.start:
                Called on interactive or batch startup after initialization.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            application.exit:
                Called just before Maya exits.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            plugin.load:
                Mapped to 'plugin.load.after'

            plugin.load.before:
                Called prior to a plugin being loaded.
                Parameters: (clientData=None)
                Signature: ([path: str], clientData) -> None

            plugin.load.after:
                Called after a plugin is loaded.
                Parameters: (clientData=None)
                Signature: ([path: str, name: str], clientData) -> None

            plugin.unload:
                Mapped to 'plugin.unload.after'.

            plugin.unload.before:
                Called prior to a plugin being unloaded.
                Parameters: (clientData=None)
                Signature: ([name: str], clientData) -> None

            plugin.unload.after:
                Called after a plugin is unloaded.
                Parameters: (clientData=None)
                Signature: ([name: str, path: str], clientData) -> None

            connection:
                Mapped to 'connection.after'.

            connection.before:
                Called before a connection is made or broken in the dependency graph.
                Parameters: (clientData=None)
                Signature: (srcPlug: MPlug, destPlug: MPlug, made: bool, clientData) -> None

            connection.after:
                Called after a connection is made or broken in the dependency graph.
                Parameters: (clientData=None)
                Signature: (srcPlug: MPlug, destPlug: MPlug, made: bool, clientData) -> None

            node.added:
                Called whenever a new node is added to the dependency graph.
                The nodeType argument allows you to specify the type of nodes that will trigger the callback.
                The default node type is "dependNode" which matches all nodes.
                Parameters: (nodeType='dependNode', clientData=None)
                Signature: (node: MObject, clientData) -> None

            node.removed:
                Called whenever a new node is removed from the dependency graph.
                The nodeType argument allows you to specify the type of nodes that will trigger the callback.
                The default node type is "dependNode" which matches all nodes.
                Parameters: (nodeType='dependNode', clientData=None)
                Signature: (node: MObject, clientData) -> None

            node.dirty:
                Called for node dirty messages.
                Parameters: (node: MObject, clientData=None)
                Signature: (node: MObject, plug: MPlug, clientData) -> None

            node.dirty.plug:
                Called for node dirty messages.
                Parameters: (node: MObject, clientData=None)
                Signature: (node: MObject, plug: MPlug, clientData) -> None

            node.name.changed:
                Called for name changed messages.
                Use a null MObject to listen for all nodes.
                Parameters: (node: MObject, clientData=None)
                Signature (node: MObject, prevName: str, clientData) -> None

            node.uuid.changed:
                Called for UUID changed messages.
                Parameters: (node: MObject, clientData=None)
                Signature (node: MObject, prevUuid: MUuid, clientData) -> None

            frame.changed:
                Callback that is called whenever the time changes in the dependency graph.
                Parameters: (clientData=None)
                Signature: (time: MTime, clientData) -> None

            frame.changed.deferred:
                Called after the time changes and after all DG nodes have been evaluated.
                Parameters: (clientData=None)
                Signature: (time: MTime, clientData) -> None

            attribute.changed:
                Called when an attribute is added or removed.
                Parameters: (node: MObject, clientData=None)
                Signature: TODO

            attribute.value.changed:
                Called for attribute value changed messages.
                The callback is disabled while Maya is in playback or scrubbing modes.
                Parameters: (node: MObject, clientData=None)
                Signature: TODO

            attribute.keyable.changed:
                Called for attribute keyable state changes.
                Return a value to accept or reject the change.
                Only one keyable change callback per attribute is allowed.
                Parameters: (plug: MPlug, clientData=None)
                Signature: TODO

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
        dgMessageWithNode = None
        nodeMessageWithNode = None

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
                    nodeMessage = om2.MNodeMessage.addUuidChangedCallback
            elif parts[2] == 'dirty':
                if parts[3] == 'plug':
                    dgMessageWithNode = om2.MNodeMessage.addNodeDirtyPlugCallback
                elif parts[3] is None:
                    dgMessageWithNode = om2.MNodeMessage.addNodeDirtyCallback
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
                nodeMessageWithNode = om2.MNodeMessage.addAttributeAddedOrRemovedCallback
            elif parts[1] == 'value':
                if parts[2] == 'changed':
                    nodeMessageWithNode = om2.MNodeMessage.addAttributeChangedCallback
            elif parts[1] == 'keyable':
                if parts[2] == 'changed':
                    nodeMessageWithNode = om2.MNodeMessage.addKeyableChangeOverride

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
        elif dgMessageWithNode is not None:
            register = partial(dgMessageWithNode, args[0])
            args = args[1:]
            unregister = om2.MMessage.removeCallback
        elif nodeMessage is not None:
            register = nodeMessage
            unregister = om2.MNodeMessage.removeCallback
        elif nodeMessageWithNode is not None:
            register = partial(nodeMessageWithNode, args[0])
            unregister = om2.MNodeMessage.removeCallback
            args = args[1:]
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
