from __future__ import absolute_import

from functools import partial, wraps

import maya.api.OpenMaya as om2
import maya.cmds as mc

from ..abstract.callbacks import AbstractCallbacks, CallbackProxy


class MayaCallbacks(AbstractCallbacks):
    def add(self, name, func, *args, **kwargs):
        """Register a callback.

        Callbacks:
            'file.new:
                Mapped to 'file.new.after'.

            file.new.before:
                Called before a File > New operation.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            file.new.before.check:
                Called prior to File > New operation, allows user to cancel action.
                Parameters: (clientData=None)
                Signature: (clientData) -> bool

            file.new.after:
                Called after a File > New operation.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            file.load:
                Mapped to 'file.load.after'.

            file.load.before:
                Called before a File > Open operation.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            file.load.before.check:
                Called prior to File > Open operation, allows user to cancel action.
                Parameters: (clientData=None)
                Signature: (clientData) -> bool

            file.load.after:
                Called after a File > Open operation.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            file.save:
                Mapped to 'file.save.after'.

            file.save.before:
                Called before a File > Save (or SaveAs) operation.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            file.save.before.check:
                Called before a File > Save (or SaveAs) operation.
                Parameters: (clientData=None)
                Signature: (clientData) -> bool

            file.save.after:
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

            render.software.cancel:
                Called when an interactive render is interrupted by the user.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            app.init:
                Called on interactive or batch startup after initialization.
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            app.exit:
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

            node.add:
                Called whenever a new node is added to the dependency graph.
                The nodeType argument allows you to specify the type of nodes that will trigger the callback.
                The default node type is "dependNode" which matches all nodes.
                Parameters: (nodeType='dependNode', clientData=None)
                Signature: (node: MObject, clientData) -> None

            node.remove:
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

            node.rename:
                Called for name changed messages.
                Use a null MObject to listen for all nodes.
                Parameters: (node: MObject, clientData=None)
                Signature: (node: MObject, prevName: str, clientData) -> None

            node.uuid.changed:
                Called for UUID changed messages.
                Parameters: (node: MObject, clientData=None)
                Signature: (node: MObject, prevUuid: MUuid, clientData) -> None

            node.uuid.changed.check:
                Called whenever a node may have its UUID changed.
                Possible causes include renaming/reading from a file.
                Parameters: (clientData=None)
                Signature: (doAction: bool, node: MObject, uuid: MUuid, clientData) -> Action
                    doAction: Whether the UUID will be applied.
                    uuid: The UUID that may be applied to the node.
                        The callback may modify this parameter.
                    Action: Enum defined in `om2.MMessage`.
                        kDefaultAction: Do not change if the UUID is used or not.
                        kDoNotDoAction: Do not use the new UUID.
                        kDoAction: Use the new UUID.

            node.destroyed:
                Called when the node is destroyed.
                Parameters: (node: MObject, clientData=None)
                Signature: (clientData) -> None

            frame.changed:
                Callback that is called whenever the time changes in the dependency graph.
                Parameters: (clientData=None)
                Signature: (time: MTime, clientData) -> None

            frame.changed.after:
                Called after the time changes and after all DG nodes have been evaluated.
                Parameters: (clientData=None)
                Signature: (time: MTime, clientData) -> None

            frame.playing:
                Called when Maya changes playing back state.
                Parameters: (clientData=None)
                Signature: (state: bool, clientData) -> None

            attribute.changed:
                Called for all attribute value changed messages.
                The callback is disabled while Maya is in playback or scrubbing modes.
                Use a null MObject to listen for all nodes.
                Parameters: (node: MObject, clientData=None)
                Signature: (msg: int, plug: MPlug, clientData) -> None

            attribute.add:
                Called when an attribute is added.
                Use a null MObject to listen for all nodes.
                Parameters: (node: MObject, clientData=None)
                Signature: (msg: int, plug: MPlug, otherPlug: MPlug, clientData) -> None

            attribute.remove:
                Called when an attribute is removed.
                Use a null MObject to listen for all nodes.
                Parameters: (node: MObject, clientData=None)
                Signature: (msg: int, plug: MPlug, otherPlug: MPlug, clientData) -> None

            attribute.value:
                Mapped to 'attribute.value.changed'

            attribute.value.changed:
                Called when an attribute value is changed.
                Use a null MObject to listen for all nodes.
                Parameters: (node: MObject, clientData=None)
                Signature: (msg: int, plug: MPlug, otherPlug: MPlug, clientData) -> None

            attribute.locked:
                Called when an attribute is locked or unlocked.
                Use a null MObject to listen for all nodes.
                Parameters: (node: MObject, clientData=None)
                Signature: (msg: int, plug: MPlug, otherPlug: MPlug, clientData) -> None

            attribute.locked.set:
                Called when an attribute is locked.
                Use a null MObject to listen for all nodes.
                Parameters: (node: MObject, clientData=None)
                Signature: (msg: int, plug: MPlug, otherPlug: MPlug, clientData) -> None

            attribute.locked.unset:
                Called when an attribute is unlocked.
                Use a null MObject to listen for all nodes.
                Parameters: (node: MObject, clientData=None)
                Signature: (msg: int, plug: MPlug, otherPlug: MPlug, clientData) -> None

            attribute.keyable:
                Called when an attribute is made keyable or unkeyable.
                Use a null MObject to listen for all nodes.
                Parameters: (node: MObject, clientData=None)
                Signature: (msg: int, plug: MPlug, otherPlug: MPlug, clientData) -> None

            attribute.keyable.set:
                Called when an attribute is made keyable.
                Use a null MObject to listen for all nodes.
                Parameters: (node: MObject, clientData=None)
                Signature: (msg: int, plug: MPlug, otherPlug: MPlug, clientData) -> None

            attribute.keyable.unset:
                Called when an attribute is made unkeyable.
                Use a null MObject to listen for all nodes.
                Parameters: (node: MObject, clientData=None)
                Signature: (msg: int, plug: MPlug, otherPlug: MPlug, clientData) -> None

            attribute.keyable.override:
                Called for attribute keyable state changes.
                Return a value to accept or reject the change.
                Only one keyable change callback per attribute is allowed.
                Parameters: (plug: MPlug, clientData=None)
                Signature: (plug: MPlug, clientData) -> bool

            undo:
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            redo:
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            selection.changed:
                Mapped to 'selection.changed.after'.

            selection.changed.before:
                Parameters: (clientData=None)
                Signature: (clientData) -> None

            selection.changed.after:
                Parameters: (clientData=None)
                Signature: (clientData) -> None

        TODO:
            'scriptjob.event'
            'scriptjob.condition'

            om2.MDGMessage.addNodeChangeUuidCheckCallback
        """
        _func = func
        parts = name.split('.') + [None, None, None, None]

        sceneMessage = None
        sceneCheckMessage = None
        sceneFileCheckMessage = None
        sceneStringArrayMessage = None
        scriptJobEvent = None
        scriptJobCondition = None
        dgMessage = None
        nodeMessage = None
        eventMessage = None
        dgMessageWithNode = None
        nodeMessageWithNode = None
        conditionName = None

        if parts[0] == 'file':
            if parts[1] == 'new':
                if parts[2] == 'before':
                    if parts[3] == 'check':
                        sceneCheckMessage = om2.MSceneMessage.kBeforeNewCheck
                    elif parts[3] is None:
                        sceneMessage = om2.MSceneMessage.kBeforeNew
                elif parts[2] in ('after', None):
                    sceneMessage = om2.MSceneMessage.kAfterNew

            elif parts[1] == 'load':
                if parts[2] == 'before':
                    if parts[3] == 'check':
                        sceneFileCheckMessage = om2.MSceneMessage.kBeforeOpenCheck
                    elif parts[3] is None:
                        sceneMessage = om2.MSceneMessage.kBeforeOpen
                elif parts[2] in ('after', None):
                    sceneMessage = om2.MSceneMessage.kAfterOpen

            elif parts[1] == 'save':
                if parts[2] == 'before':
                    if parts[3] == 'check':
                        sceneCheckMessage = om2.MSceneMessage.kBeforeSaveCheck
                    elif parts[3] is None:
                        sceneMessage = om2.MSceneMessage.kBeforeSave
                elif parts[2] in ('after', None):
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
                elif parts[2] == 'cancel':
                    sceneMessage = om2.MSceneMessage.kSoftwareRenderInterrupted

        elif parts[0] == 'app':
            if parts[1] == 'init':
                sceneMessage = om2.MSceneMessage.kMayaInitialized
            elif parts[1] == 'exit':
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
            if parts[1] == 'add':
                dgMessage = om2.MDGMessage.addNodeAddedCallback
            elif parts[1] == 'remove':
                # if parts[2] == 'before':
                #     nodeMessageWithNode = om2.MNodeMessage.addNodePreRemovalCallback
                # elif parts[2] in ('after', None):
                #     dgMessage = om2.MDGMessage.addNodeRemovedCallback
                dgMessage = om2.MDGMessage.addNodeRemovedCallback
            elif parts[1] == 'rename':
                nodeMessageWithNode = om2.MNodeMessage.addNameChangedCallback
            elif parts[1] == 'uuid':
                if parts[2] == 'changed':
                    if parts[3] == 'check':
                        dgMessage = om2.MDGMessage.addNodeChangeUuidCheckCallback
                    elif parts[3] is None:
                        nodeMessageWithNode = om2.MNodeMessage.addUuidChangedCallback
            elif parts[1] == 'dirty':
                if parts[2] == 'plug':
                    nodeMessageWithNode = om2.MNodeMessage.addNodeDirtyPlugCallback
                elif parts[2] is None:
                    nodeMessageWithNode = om2.MNodeMessage.addNodeDirtyCallback
            elif parts[1] == 'destroyed':
                nodeMessageWithNode = om2.MNodeMessage.addNodeDestroyedCallback

        elif parts[0] == 'frame':
            if parts[1] == 'changed':
                if parts[2] is None:
                    # eventMessage = 'timeChanged'
                    dgMessage = om2.MDGMessage.addTimeChangeCallback
                elif parts[2] == 'after':
                    dgMessage = om2.MDGMessage.addForceUpdateCallback
            elif parts[1] == 'playing':
                conditionName = 'playingBack'

        elif parts[0] == 'attribute':
            def filterByMsg(allowedFilter):
                """Avoid running a callback when a message doesn't match."""
                @wraps(_func)
                def wrapper(msg, plug, otherPlug, clientData):
                    if msg & allowedFilter:
                        _func(msg, plug, otherPlug, clientData)
                return wrapper

            if parts[1] == 'changed':
                nodeMessageWithNode = om2.MNodeMessage.addAttributeChangedCallback

            elif parts[1] == 'add':
                nodeMessageWithNode = om2.MNodeMessage.addAttributeChangedCallback
                func = filterByMsg(om2.MNodeMessage.kAttributeAdded)

            elif parts[1] == 'remove':
                nodeMessageWithNode = om2.MNodeMessage.addAttributeChangedCallback
                func = filterByMsg(om2.MNodeMessage.kAttributeRemoved)

            elif parts[1] == 'value':
                if parts[2] in ('changed', None):
                    nodeMessageWithNode = om2.MNodeMessage.addAttributeChangedCallback
                    func = filterByMsg(om2.MNodeMessage.kAttributeSet)

            elif parts[1] == 'locked':
                if parts[2] == 'set':
                    nodeMessageWithNode = om2.MNodeMessage.addAttributeChangedCallback
                    func = filterByMsg(om2.MNodeMessage.kAttributeLocked)
                elif parts[2] == 'unset':
                    nodeMessageWithNode = om2.MNodeMessage.addAttributeChangedCallback
                    func = filterByMsg(om2.MNodeMessage.kAttributeUnlocked)
                elif parts[2] is None:
                    nodeMessageWithNode = om2.MNodeMessage.addAttributeChangedCallback
                    func = filterByMsg(om2.MNodeMessage.kAttributeLocked | om2.MNodeMessage.kAttributeUnlocked)

            elif parts[1] == 'keyable':
                if parts[2] == 'set':
                    nodeMessageWithNode = om2.MNodeMessage.addAttributeChangedCallback
                    func = filterByMsg(om2.MNodeMessage.kAttributeKeyable)
                elif parts[2] == 'unset':
                    nodeMessageWithNode = om2.MNodeMessage.addAttributeChangedCallback
                    func = filterByMsg(om2.MNodeMessage.kAttributeUnkeyable)
                elif parts[2] is None:
                    nodeMessageWithNode = om2.MNodeMessage.addAttributeChangedCallback
                    func = filterByMsg(om2.MNodeMessage.kAttributeKeyable | om2.MNodeMessage.kAttributeUnkeyable)
                elif parts[2] == 'override':
                    nodeMessageWithNode = om2.MNodeMessage.addKeyableChangeOverride

            elif parts[1] == 'rename':
                nodeMessageWithNode = om2.MNodeMessage.addAttributeChangedCallback
                func = filterByMsg(om2.MNodeMessage.kAttributeRenamed)

        elif parts[0] == 'undo':
            eventMessage = 'Undo'

        elif parts[0] == 'redo':
            eventMessage = 'Redo'

        elif parts[0] == 'selection':
            if parts[1] == 'changed':
                if parts[2] == 'before':
                    eventMessage = 'PreSelectionChangedTriggered'
                elif parts[2] in ('after', None):
                    eventMessage = 'SelectionChanged'

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
            try:
                register = partial(dgMessageWithNode, args[0])
            except IndexError:
                raise ValueError('missing required argument')
            args = args[1:]
            unregister = om2.MMessage.removeCallback
        elif nodeMessage is not None:
            register = nodeMessage
            unregister = om2.MNodeMessage.removeCallback
        elif nodeMessageWithNode is not None:
            try:
                register = partial(nodeMessageWithNode, args[0])
            except IndexError:
                raise ValueError('missing required argument')
            unregister = om2.MNodeMessage.removeCallback
            args = args[1:]
        elif scriptJobEvent is not None:
            register = lambda func, *args, **kwargs: mc.scriptJob(event=[scriptJobEvent, func], *args, **kwargs)
            unregister = lambda callbackID: mc.scriptJob(kill=callbackID)
        elif scriptJobCondition is not None:
            register = lambda func, *args, **kwargs: mc.scriptJob(conditionChange=[scriptJobCondition, func], *args, **kwargs)
            unregister = lambda callbackID: mc.scriptJob(kill=callbackID)
        elif eventMessage is not None:
            register = partial(om2.MEventMessage.addEventCallback, eventMessage)
            unregister = om2.MMessage.removeCallback
        elif conditionName is not None:
            register = partial(om2.MConditionMessage.addConditionCallback, conditionName)
            unregister = om2.MConditionMessage.removeCallback
        else:
            return super(MayaCallbacks, self).add(name, func, *args, **kwargs)

        # Directly passing in the `nodeType` argument causes an error
        if 'nodeType' in kwargs:
            args = list(args) + [kwargs.pop('nodeType')]

        callback = CallbackProxy(name, register, unregister, func, args, kwargs).register()
        self._callbacks.append(callback)
        return callback

    def addSceneMessage(self, msg, func, clientData=None):
        """Add a scene callback.

        Parameters:
            msg (int): Scene message.
                kSceneUpdate
                kBeforeNew
                kAfterNew
                kBeforeImport
                kAfterImport
                kBeforeOpen
                kAfterOpen
                kBeforeExport
                kAfterExport
                kBeforeSave
                kAfterSave
                kBeforeCreateReference
                kAfterCreateReference
                kBeforeRemoveReference
                kAfterRemoveReference
                kBeforeImportReference
                kAfterImportReference
                kBeforeExportReference
                kAfterExportReference
                kBeforeUnloadReference
                kAfterUnloadReference
                kBeforeLoadReference
                kAfterLoadReference
                kBeforeSoftwareRender
                kAfterSoftwareRender
                kBeforeSoftwareFrameRender
                kAfterSoftwareFrameRender
                kSoftwareRenderInterrupted
                kMayaInitialized
                kMayaExiting

            func (callable): Callback function.
                Signature: (clientData: Any) -> None

            clientData (any): Data to pass to the callback.
        """
        register = partial(om2.MSceneMessage.addCallback, msg)
        unregister = om2.MSceneMessage.removeCallback
        callback = CallbackProxy(func.__name__, register, unregister,
                                 func, (), {'clientData': clientData}).register()
        self._callbacks.append(callback)
        return callback

    def addSceneCheckMessage(self, msg, func, clientData=None):
        """Add a scene callback.

        Parameters:
            msg (int): Scene check message.
                om2.MSceneMessage.kBeforeNewCheck
                om2.MSceneMessage.kBeforeImportCheck
                om2.MSceneMessage.kBeforeOpenCheck
                om2.MSceneMessage.kBeforeExportCheck
                om2.MSceneMessage.kBeforeSaveCheck
                om2.MSceneMessage.kBeforeCreateReferenceCheck
                om2.MSceneMessage.kBeforeLoadReferenceCheck

            func (callable): Callback function.
                Signature: (clientData: Any) -> bool

            clientData (any): Data to pass to the callback.
        """
        register = partial(om2.MSceneMessage.addCheckCallback, msg)
        unregister = om2.MSceneMessage.removeCallback
        callback = CallbackProxy(func.__name__, register, unregister,
                                 func, (), {'clientData': clientData}).register()
        self._callbacks.append(callback)
        return callback

    def addSceneFileCheckMessage(self, msg, func, clientData=None):
        """Add a scene file check callback.

        Parameters:
            msg (int): Scene file check message.
                om2.MSceneMessage.kBeforeImportCheck
                om2.MSceneMessage.kBeforeOpenCheck
                om2.MSceneMessage.kBeforeExportCheck
                om2.MSceneMessage.kBeforeCreateReferenceCheck
                om2.MSceneMessage.kBeforeLoadReferenceCheck

            func (callable): Callback function.
                Signature: (file: MFileObject, clientData: Any) -> bool

            clientData (any): Data to pass to the callback.
        """
        register = partial(om2.MSceneMessage.addCheckFileCallback, msg)
        unregister = om2.MSceneMessage.removeCallback
        callback = CallbackProxy(func.__name__, register, unregister,
                                 func, (), {'clientData': clientData}).register()
        self._callbacks.append(callback)
        return callback

    def addSceneStringArrayMessage(self, msg, func, clientData=None):
        """Add a scene string array callback.

        Parameters:
            msg (int): Scene message.
                kBeforePluginLoad (path)
                kAfterPluginLoad (path, name)
                kBeforePluginUnload (name)
                kAfterPluginUnload (name, path)

            func (callable): Callback function.
                Signature: (strs: List[str]) -> None

            clientData (any): Data to pass to the callback.
        """
        register = partial(om2.MSceneMessage.addCheckFileCallback, msg)
        unregister = om2.MSceneMessage.removeCallback
        callback = CallbackProxy(func.__name__, register, unregister,
                                 func, (), {'clientData': clientData}).register()
        self._callbacks.append(callback)
        return callback

    def addEventMessage(self, eventName, func, clientData=None):
        """Add an event callback.

        Parameters:
            eventName (str): Name of the event.
                To view all available events, use
                `om2.MEventMessage.getEventNames()`.

            func (callable): Callback function.
                Signature: (clientData: Any) -> None

            clientData (any): Data to pass to the callback.
        """
        register = partial(om2.MEventMessage.addEventCallback, eventName)
        unregister = om2.MMessage.removeCallback
        callback = CallbackProxy(func.__name__, register, unregister,
                                 func, (), {'clientData': clientData}).register()
        self._callbacks.append(callback)
        return callback

    def registerScriptJobEvent(self, msg, func, group=None, runOnce=False):
        mc.scriptJob(runOnce=runOnce, event=[msg, func])

    def registerScriptJobCondition(self, msg, func, group=None, runOnce=False):
        mc.scriptJob(runOnce=runOnce, conditionChange=[msg, func])
