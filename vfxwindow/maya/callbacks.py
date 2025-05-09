from __future__ import absolute_import

from functools import partial

import maya.OpenMaya as om
import maya.api.OpenMaya as om2
import maya.cmds as mc

from ..abstract.callbacks import AbstractCallbacks, CallbackProxy, CallbackAliases


class MayaCallbacks(AbstractCallbacks):
    """Maya callbacks.

    By default the callbacks use `maya.api.OpenMaya`.
    The callback group 'legacy' has been assigned `maya.OpenMaya`.
    For safety, each API has its own set of aliases that will be used.

    Callbacks:
        file.new:
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
            Signature: (file: MFileObject, clientData) -> bool

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

        file.import:
            Mapped to 'file.import.after'.

        file.import.before:
            Called before a File > Import operation.
            Parameters: (clientData=None)
            Signature: (clientData) -> None

        file.import.before.check:
            Called prior to File > Import operation, allows user to cancel action.
            Parameters: (clientData=None)
            Signature: (file: MFileObject, clientData) -> bool

        file.import.after:
            Called after a File > Import operation.
            Parameters: (clientData=None)
            Signature: (clientData) -> None

        file.export:
            Mapped to 'file.export.after'.

        file.export.before:
            Called before a File > Export operation.
            Parameters: (clientData=None)
            Signature: (clientData) -> None

        file.export.before.check:
            Called prior to File > Export operation, allows user to cancel action.
            Parameters: (clientData=None)
            Signature: (file: MFileObject, clientData) -> bool

        file.export.after:
            Called after a File > Export operation.
            Parameters: (clientData=None)
            Signature: (clientData) -> None

        file.reference:
            Mapped to 'file.reference.after'.

        file.reference.before:
            Called before a File > CreateReference / LoadReference operation.
            Parameters: (clientData=None)
            Signature: (clientData) -> None

        file.reference.after:
            Called after a File > CreateReference / LoadReference operation.
            Parameters: (clientData=None)
            Signature: (clientData) -> None

        file.reference.create:
            Mapped to 'file.reference.create.after'.

        file.reference.create.before:
            Called before a File > CreateReference operation.
            Parameters: (clientData=None)
            Signature: (clientData) -> None

        file.reference.create.before.check:
            Called prior to a File > CreateReference operation, allows user to cancel action.
            Parameters: (clientData=None)
            Signature: (file: MFileObject, clientData) -> bool

        file.reference.create.after:
            Called after a File > CreateReference operation.
            Parameters: (clientData=None)
            Signature: (clientData) -> None

        file.reference.remove:
            Mapped to 'file.reference.remove.after'.

        file.reference.remove.before:
            Called before a File > RemoveReference operation.
            Parameters: (clientData=None)
            Signature: (clientData) -> None

        file.reference.remove.after:
            Called after a File > RemoveReference operation.
            Parameters: (clientData=None)
            Signature: (clientData) -> None

        file.reference.load:
            Mapped to 'file.reference.load.after'.

        file.reference.load.before:
            Called before a File > LoadReference operation.
            Parameters: (clientData=None)
            Signature: (clientData) -> None

        file.reference.load.before.check:
            Called before a File > LoadReference operation, allows user to cancel action.
            Parameters: (clientData=None)
            Signature: (file: MFileObject, clientData) -> bool

        file.reference.load.after:
            Called after a File > LoadReference operation.
            Parameters: (clientData=None)
            Signature: (clientData) -> None

        file.reference.unload:
            Mapped to 'file.reference.unload.after'.

        file.reference.unload.before:
            Called before a File > UnloadReference operation.
            Parameters: (clientData=None)
            Signature: (clientData) -> None

        file.reference.unload.after:
            Called after a File > UnloadReference operation.
            Parameters: (clientData=None)
            Signature: (clientData) -> None

        file.reference.import:
            Mapped to 'file.reference.import.after'.

        file.reference.import.before:
            Called before a File > ImportReference operation.
            Parameters: (clientData=None)
            Signature: (clientData) -> None

        file.reference.import.after:
            Called after a File > ImportReference operation.
            Parameters: (clientData=None)
            Signature: (clientData) -> None

        file.reference.export:
            Mapped to 'file.reference.export.after'

        file.reference.export.before:
            Called before a File > ExportReference operation.
            Parameters: (clientData=None)
            Signature: (clientData) -> None

        file.reference.export.after:
            Called after a File > ExportReference operation.
            Parameters: (clientData=None)
            Signature: (clientData) -> None

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

        node.create:
            Called whenever a new node is added to the dependency graph.
            The nodeType argument allows you to specify the type of nodes that will trigger the callback.
            The default node type is "dependNode" which matches all nodes.
            Parameters: (nodeType='dependNode', clientData=None)
            Signature: (node: MObject, clientData) -> None

        node.remove:
            Called whenever a new node is removed from the dependency graph.
            The nodeType argument allows you to specify the type of nodes that will trigger the callback.
            The default node type is "dependNode" which matches all nodes.
            This is used instead of `MNodeMessage.addNodePreRemovalCallback` and
            `MNodeMessage.aboutToDelete` as they are much more specific and have extra rules.
            Parameters: (nodeType='dependNode', clientData=None)
            Signature: (node: MObject, clientData) -> None

        node.name.changed:
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
                Action: Enum defined in `MMessage`.
                    kDefaultAction: Do not change if the UUID is used or not.
                    kDoNotDoAction: Do not use the new UUID.
                    kDoAction: Use the new UUID.

        frame.changed:
            Callback that is called whenever the time changes in the dependency graph.
            Parameters: (clientData=None)
            Signature: (time: MTime, clientData) -> None

        frame.changed.after:
            Called after the time changes and after all DG nodes have been evaluated.
            Parameters: (clientData=None)
            Signature: (time: MTime, clientData) -> None

        frame.changed.deferred:
            Called after the time has finished changing.
            Scrubbing the timeline will only call this once on mouse release.
            Parameters: ()
            Signature: () -> None

        frame.range.changed:
            Called when the animation range is changed.
            This does not trigger when editing the time slider range.
            Parameters: (clientData=None)
            Signature: (clientData) -> None

        playback:
            Called when Maya starts or stops playing back.
            Parameters: (clientData=None)
            Signature: (state: bool, clientData) -> None

        playback.start:
            Called when Maya starts playing back.
            Parameters: (clientData=None)
            Signature: (state: bool, clientData) -> None

        playback.stop:
            Called when Maya stops playing back.
            Parameters: (clientData=None)
            Signature: (state: bool, clientData) -> None

        playback.range.changed:
            Mapped to 'playback.range.changed.after'

        playback.range.changed.before:
            Called before the time slider range changes.
            This does not trigger when editing the animation range.
            Parameters: (clientData=None)
            Signature: (clientData) -> None

        playback.range.changed.after:
            Called after the time slider range changes.
            This does not trigger when editing the animation range.
            Parameters: (clientData=None)
            Signature: (clientData) -> None

        playback.speed.changed:
            Called when the playback speed (fps) is updated.
            Parameters: (clientData=None)
            Signature: (clientData) -> None

        playback.mode.changed:
            Called when the playback mode (loop/play once) is updated.
            Parameters: (clientData=None)
            Signature: (clientData) -> None

        attribute.changed:
            Called for all attribute value changed messages.
            The callback is disabled while Maya is in playback or scrubbing modes.
            Use a null MObject to listen for all nodes.
            Parameters: (node: MObject, clientData=None)
            Signature: (msg: int, plug: MPlug, otherPlug: MPlug, clientData) -> None

        attribute.create:
            Called when an attribute is added.
            Use a null MObject to listen for all nodes.
            Parameters: (node: MObject, clientData=None)
            Signature: (msg: int, plug: MPlug, otherPlug: MPlug, clientData) -> None

        attribute.remove:
            Called when an attribute is removed.
            Use a null MObject to listen for all nodes.
            Parameters: (node: MObject, clientData=None)
            Signature: (msg: int, plug: MPlug, otherPlug: MPlug, clientData) -> None

        attribute.name.changed:
            Called when an attribute name is changed.
            Use a null MObject to listen for all nodes.
            Parameters: (node: MObject, clientData=None)
            Signature: (msg: int, plug: MPlug, otherPlug: MPlug, clientData) -> None

        attribute.value.changed:
            Called when an attribute value is changed.
            Use a null MObject to listen for all nodes.
            Parameters: (node: MObject, clientData=None)
            Signature: (msg: int, plug: MPlug, otherPlug: MPlug, clientData) -> None

        attribute.lock.changed:
            Called when an attribute is locked or unlocked.
            Use a null MObject to listen for all nodes.
            Parameters: (node: MObject, clientData=None)
            Signature: (msg: int, plug: MPlug, otherPlug: MPlug, clientData) -> None

        attribute.lock.set:
            Called when an attribute is locked.
            Use a null MObject to listen for all nodes.
            Parameters: (node: MObject, clientData=None)
            Signature: (msg: int, plug: MPlug, otherPlug: MPlug, clientData) -> None

        attribute.lock.unset:
            Called when an attribute is unlocked.
            Use a null MObject to listen for all nodes.
            Parameters: (node: MObject, clientData=None)
            Signature: (msg: int, plug: MPlug, otherPlug: MPlug, clientData) -> None

        attribute.keyable.changed:
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

    Unimplemented:
        MNodeMessage.addNodePreRemovalCallback | MNodeMessage.aboutToDelete:
            Both of these have very specific purposes for running before
            a node is removed. `addNodePreRemovalCallback` is called
            even during a redo, and cannot perform any DG operations.
            `aboutToDelete` is called once on deletion, and provides a
            DG modifier for any operation so that it works with the
            undo queue.
            Because both of these have such specific uses, and the fact
            that `node.create` uses `addNodeAddedCallback`, it makes
            sense for `node.remove` to use `addNodeRemovedCallback`
            rather than than any of these.

            If absolutely needed, use the `addMessage` method.
            >>> cb.addMessage(partial(MNodeMessage.addNodePreRemovalCallback, node), func)

            Or create your own alias:
            >>> cb.aliases['custom.nodePreRemoval'] = (
            ...     lambda func, node, clientData=None: om2.MNodeMessage.addNodePreRemovalCallback(node, func, clientData),
            ...     lambda callbackID: self.api.MMessage.removeCallback(callbackID),
            ... )
            >>> cb.add('custom.nodePreRemoval', func, node)

        MNodeMessage.addNodeDirtyCallback:
            Called for node dirty messages.
            Parameters: (node: MObject, clientData=None)
            Signature: (node: MObject, plug: MPlug, clientData) -> None

        MNodeMessage.addNodeDirtyPlugCallback:
            Called for node plug dirty messages.
            Parameters: (node: MObject, clientData=None)
            Signature: (node: MObject, plug: MPlug, clientData) -> None

        MNodeMessage.addNodeDestroyedCallback:
            Called when the node is destroyed.
            Parameters: (node: MObject, clientData=None)
            Signature: (clientData) -> None

        renderLayerChange | renderLayerManagerChange | displayLayerChange:
            Some events are simply shorthand for attribute change callbacks.

            # Directly use `callbacks.addEventMessage`
            >>> def layerChanged(clientData=None):
            ...     print('Render layer changed')
            >>> self.callbacks.addEventMessage('renderLayerManagerChange', layerChanged)

            # Use `attribute.changed` callback
            >>> def rlmChanged(msg, plug, otherPlug, clientData):
            ...     if not msg & om2.MNodeMessage.kAttributeSet: return
            ...     if plug.name() != 'renderLayerManager.currentRenderLayer': return
            ...     layerChanged()
            >>> selection = om2.MSelectionList()
            >>> selection.add('renderLayerManager')
            >>> callbacks.add('attribute.changed', rlmChanged, selection.getDependNode(0))
    """

    def __init__(self, *args, **kwargs):
        super(MayaCallbacks, self).__init__(*args, **kwargs)
        self._api = om2
        self._mayaAliases = [None, self.aliases]

    @property
    def api(self):
        """Get Maya's API."""
        return self._api

    @api.setter
    def api(self, api):
        """Set the Maya API version to use.
        The alias set is switched out depending on the API version.
        """
        if api is om:
            aliases = self._mayaAliases[0]
        elif api is om2:
            aliases = self._mayaAliases[1]
        else:
            raise NotImplementedError(api.__name__)
        if aliases is None:
            self.aliases = CallbackAliases()
            self._setupAliases()
        else:
            self.aliases = aliases
        self._api = api

    def _new(self):
        new = super(MayaCallbacks, self)._new()
        new.api = self.api
        new._mayaAliases = self._mayaAliases
        return new

    def _setupAliases(self):
        """Setup Maya callback aliases."""
        def unregMsg(callbackID):
            self.api.MMessage.removeCallback(callbackID)
        def unregMultipleMsg(callbackIDs):
            for callbackID in callbackIDs:
                unregMsg(callbackID)
        def unregSJ(callbackID):
            mc.scriptJob(kill=callbackID)

        def beforeNew(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kBeforeNew, func, clientData)
        self.aliases['file.new.before'] = (beforeNew, unregMsg)

        def beforeNewCheck(func, clientData=None):
            return self.api.MSceneMessage.addCheckCallback(self.api.MSceneMessage.kBeforeNewCheck, func, clientData)
        self.aliases['file.new.before.check'] = (beforeNewCheck, unregMsg)

        def afterNew(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kAfterNew, func, clientData)
        self.aliases['file.new'] = self.aliases['file.new.after'] = (afterNew, unregMsg)

        def beforeLoad(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kBeforeOpen, func, clientData)
        self.aliases['file.load.before'] = (beforeLoad, unregMsg)

        def beforeLoadCheck(func, clientData=None):
            return self.api.MSceneMessage.addCheckFileCallback(self.api.MSceneMessage.kBeforeOpenCheck, func, clientData)
        self.aliases['file.load.before.check'] = (beforeLoadCheck, unregMsg)

        def afterLoad(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kAfterOpen, func, clientData)
        self.aliases['file.load'] = self.aliases['file.load.after'] = (afterLoad, unregMsg)

        def beforeSave(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kBeforeSave, func, clientData)
        self.aliases['file.save.before'] = (beforeSave, unregMsg)

        def beforeSaveCheck(func, clientData=None):
            return self.api.MSceneMessage.addCheckCallback(self.api.MSceneMessage.kBeforeSaveCheck, func, clientData)
        self.aliases['file.save.before.check'] = (beforeSaveCheck, unregMsg)

        def afterSave(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kAfterSave, func, clientData)
        self.aliases['file.save'] = self.aliases['file.save.after'] = (afterSave, unregMsg)

        def beforeImport(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kBeforeImport, func, clientData)
        self.aliases['file.import.before'] = (beforeImport, unregMsg)

        def beforeImportCheck(func, clientData=None):
            return self.api.MSceneMessage.addCheckFileCallback(self.api.MSceneMessage.kBeforeImportCheck, func, clientData)
        self.aliases['file.import.before.check'] = (beforeImportCheck, unregMsg)

        def afterImport(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kAfterImport, func, clientData)
        self.aliases['file.import'] = self.aliases['file.import.after'] = (afterImport, unregMsg)

        def beforeExport(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kBeforeExport, func, clientData)
        self.aliases['file.export.before'] = (beforeExport, unregMsg)

        def beforeExportCheck(func, clientData=None):
            return self.api.MSceneMessage.addCheckFileCallback(self.api.MSceneMessage.kBeforeExportCheck, func, clientData)
        self.aliases['file.export.before.check'] = (beforeExportCheck, unregMsg)

        def afterExport(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kAfterExport, func, clientData)
        self.aliases['file.export'] = self.aliases['file.export.after'] = (afterExport, unregMsg)

        def beforeRef(func, clientData=None):
            return [
                self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kBeforeCreateReference, func, clientData),
                self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kBeforeLoadReference, func, clientData),
            ]
        self.aliases['file.reference.before'] = (beforeRef, unregMultipleMsg)

        def afterRef(func, clientData=None):
            return [
                self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kAfterCreateReference, func, clientData),
                self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kAfterLoadReference, func, clientData),
            ]
        self.aliases['file.reference'] = self.aliases['file.reference.after'] = (afterRef, unregMultipleMsg)

        def refCreateBefore(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kBeforeCreateReference, func, clientData)
        self.aliases['file.reference.create.before'] = (refCreateBefore, unregMsg)

        def refCreateBeforeCheck(func, clientData=None):
            return self.api.MSceneMessage.addCheckFileCallback(self.api.MSceneMessage.kBeforeCreateReferenceCheck, func, clientData)
        self.aliases['file.reference.create.before.check'] = (refCreateBeforeCheck, unregMsg)

        def refCreateAfter(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kAfterCreateReference, func, clientData)
        self.aliases['file.reference.create'] = self.aliases['file.reference.create.after'] = (refCreateAfter, unregMsg)

        def refRemoveBefore(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kBeforeRemoveReference, func, clientData)
        self.aliases['file.reference.remove.before'] = (refRemoveBefore, unregMsg)

        def refRemoveAfter(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kAfterRemoveReference, func, clientData)
        self.aliases['file.reference.remove'] = self.aliases['file.reference.remove.after'] = (refRemoveAfter, unregMsg)

        def refLoadBefore(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kBeforeLoadReference, func, clientData)
        self.aliases['file.reference.load.before'] = (refLoadBefore, unregMsg)

        def refLoadBeforeCheck(func, clientData=None):
            return self.api.MSceneMessage.addCheckFileCallback(self.api.MSceneMessage.kBeforeLoadReferenceCheck, func, clientData)
        self.aliases['file.reference.load.before.check'] = (refLoadBeforeCheck, unregMsg)

        def refLoadAfter(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kAfterLoadReference, func, clientData)
        self.aliases['file.reference.load'] = self.aliases['file.reference.load.after'] = (refLoadAfter, unregMsg)

        def refUnloadBefore(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kBeforeUnloadReference, func, clientData)
        self.aliases['file.reference.unload.before'] = (refUnloadBefore, unregMsg)

        def refUnloadAfter(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kAfterUnloadReference, func, clientData)
        self.aliases['file.reference.unload'] = self.aliases['file.reference.unload.after'] = (refUnloadAfter, unregMsg)

        def refImportBefore(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kBeforeImportReference, func, clientData)
        self.aliases['file.reference.import.before'] = (refImportBefore, unregMsg)

        def refImportAfter(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kAfterImportReference, func, clientData)
        self.aliases['file.reference.import'] = self.aliases['file.reference.import.after'] = (refImportAfter, unregMsg)

        def refExportBefore(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kBeforeExportReference, func, clientData)
        self.aliases['file.reference.export.before'] = (refExportBefore, unregMsg)

        def refExportAfter(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kAfterExportReference, func, clientData)
        self.aliases['file.reference.export'] = self.aliases['file.reference.export.after'] = (refExportAfter, unregMsg)

        def renderSoftwareBefore(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kBeforeSoftwareRender, func, clientData)
        self.aliases['render.software.before'] = (renderSoftwareBefore, unregMsg)

        def renderSoftwareAfter(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kAfterSoftwareRender, func, clientData)
        self.aliases['render.software'] = self.aliases['render.software.after'] = (renderSoftwareAfter, unregMsg)

        def renderSoftwareFrameBefore(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kBeforeSoftwareFrameRender, func, clientData)
        self.aliases['render.software.frame.before'] = (renderSoftwareFrameBefore, unregMsg)

        def renderSoftwareFrameAfter(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kAfterSoftwareFrameRender, func, clientData)
        self.aliases['render.software.frame'] = self.aliases['render.software.frame.after'] = (renderSoftwareFrameAfter, unregMsg)

        def renderSoftwareCancel(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kSoftwareRenderInterrupted, func, clientData)
        self.aliases['render.software.cancel'] = (renderSoftwareCancel, unregMsg)

        def appInit(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kMayaInitialized, func, clientData)
        self.aliases['app.init'] = (appInit, unregMsg)

        def appExit(func, clientData=None):
            return self.api.MSceneMessage.addCallback(self.api.MSceneMessage.kMayaExiting, func, clientData)
        self.aliases['app.exit'] = (appExit, unregMsg)

        def pluginLoadBefore(func, clientData=None):
            return self.api.MSceneMessage.addStringArrayCallback(self.api.MSceneMessage.kBeforePluginLoad, func, clientData)
        self.aliases['plugin.load.before'] = (pluginLoadBefore, unregMsg)

        def pluginLoadAfter(func, clientData=None):
            return self.api.MSceneMessage.addStringArrayCallback(self.api.MSceneMessage.kAfterPluginLoad, func, clientData)
        self.aliases['plugin.load'] = self.aliases['plugin.load.after'] = (pluginLoadAfter, unregMsg)

        def pluginUnloadBefore(func, clientData=None):
            return self.api.MSceneMessage.addStringArrayCallback(self.api.MSceneMessage.kBeforePluginUnload, func, clientData)
        self.aliases['plugin.unload.before'] = (pluginUnloadBefore, unregMsg)

        def pluginUnloadAfter(func, clientData=None):
            return self.api.MSceneMessage.addStringArrayCallback(self.api.MSceneMessage.kAfterPluginUnload, func, clientData)
        self.aliases['plugin.unload'] = self.aliases['plugin.unload.after'] = (pluginUnloadAfter, unregMsg)

        def connectionBefore(func, clientData=None):
            return self.api.MDGMessage.addPreConnectionCallback(func, clientData)
        self.aliases['connection.before'] = (connectionBefore, unregMsg)

        def connectionAfter(func, clientData=None):
            return self.api.MDGMessage.addConnectionCallback(func, clientData)
        self.aliases['connection'] = self.aliases['connection.after'] = (connectionAfter, unregMsg)

        def nodeAdd(func, nodeType='dependNode', clientData=None):
            return self.api.MDGMessage.addNodeAddedCallback(func, nodeType, clientData)
        self.aliases['node.create'] = (nodeAdd, unregMsg)

        def nodeRemove(func, nodeType='dependNode', clientData=None):
            return self.api.MDGMessage.addNodeRemovedCallback(func, nodeType, clientData)
        self.aliases['node.remove'] = (nodeRemove, unregMsg)

        def nodeNameChange(func, node=None, clientData=None):
            if node is None:
                node = self.api.MObject.kNullObj
            return self.api.MNodeMessage.addNameChangedCallback(node, func, clientData)
        self.aliases['node.name.changed'] = (nodeNameChange, unregMsg)

        def nodeUuidChange(func, node=None, clientData=None):
            if node is None:
                node = self.api.MObject.kNullObj
            return self.api.MNodeMessage.addUuidChangedCallback(node, func, clientData)
        self.aliases['node.uuid.changed'] = (nodeUuidChange, unregMsg)

        def nodeUuidChangeCheck(func, clientData=None):
            return self.api.MDGMessage.addNodeChangeUuidCheckCallback(func, clientData)
        self.aliases['node.uuid.changed.check'] = (nodeUuidChangeCheck, unregMsg)

        def frameChange(func, clientData=None):
            return self.api.MDGMessage.addTimeChangeCallback(func, clientData)
        self.aliases['frame.changed'] = (frameChange, unregMsg)

        def frameChangeAfter(func, clientData=None):
            return self.api.MDGMessage.addForceUpdateCallback(func, clientData)
        self.aliases['frame.changed.after'] = (frameChangeAfter, unregMsg)

        def frameChangeDefer(func):
            return mc.scriptJob(event=['timeChanged', func], runOnce=False)
        self.aliases['frame.changed.deferred'] = (frameChangeDefer, unregSJ)

        def frameRangeChange(func, clientData=None):
            return self.api.MEventMessage.addEventCallback('playbackRangeSliderChanged', func, clientData)
        self.aliases['frame.range.changed'] = (frameRangeChange, unregMsg)

        def playbackRangeChangeBefore(func, clientData=None):
            return self.api.MEventMessage.addEventCallback('playbackRangeAboutToChange', func, clientData)
        self.aliases['playback.range.changed.before'] = (playbackRangeChangeBefore, unregMsg)

        def playbackRangeChangeAfter(func, clientData=None):
            return self.api.MEventMessage.addEventCallback('playbackRangeChanged', func, clientData)
        self.aliases['playback.range.changed'] = self.aliases['playback.range.changed.after'] = (playbackRangeChangeAfter, unregMsg)

        def playbackStateChange(func, clientData=None):
            return self.api.MConditionMessage.addConditionCallback('playingBack', func, clientData)
        self.aliases['playback'] = (playbackStateChange, unregMsg)
        self.aliases['playback.start'] = (playbackStateChange, unregMsg, lambda state, clientData: state)
        self.aliases['playback.stop'] = (playbackStateChange, unregMsg, lambda state, clientData: not state)

        def playbackSpeedChange(func, clientData=None):
            return self.api.MEventMessage.addEventCallback('playbackSpeedChanged', func, clientData)
        self.aliases['playback.speed.changed'] = (playbackSpeedChange, unregMsg)

        def playbackModeChange(func, clientData=None):
            return self.api.MEventMessage.addEventCallback('playbackModeChanged', func, clientData)
        self.aliases['playback.mode.changed'] = (playbackModeChange, unregMsg)

        def attributeChange(func, node=None, clientData=None):
            if node is None:
                node = self.api.MObject.kNullObj
            return self.api.MNodeMessage.addAttributeChangedCallback(node, func, clientData)
        self.aliases['attribute.changed'] = (attributeChange, unregMsg)

        def attributeAddIntercept(msg, plug, otherPlug, clientData):
            return not msg & self.api.MNodeMessage.kAttributeAdded
        self.aliases['attribute.create'] = (attributeChange, unregMsg, attributeAddIntercept)

        def attributeRemoveIntercept(msg, plug, otherPlug, clientData):
            return not msg & self.api.MNodeMessage.kAttributeRemoved
        self.aliases['attribute.remove'] = (attributeChange, unregMsg, attributeRemoveIntercept)

        def attributeValueChangeIntercept(msg, plug, otherPlug, clientData):
            return not msg & self.api.MNodeMessage.kAttributeSet
        self.aliases['attribute.value.changed'] = (attributeChange, unregMsg, attributeValueChangeIntercept)

        def attributeLockChangeIntercept(msg, plug, otherPlug, clientData):
            return not msg & (self.api.MNodeMessage.kAttributeLocked | self.api.MNodeMessage.kAttributeUnlocked)
        self.aliases['attribute.lock.changed'] = (attributeChange, unregMsg, attributeLockChangeIntercept)

        def attributeLockSetIntercept(msg, plug, otherPlug, clientData):
            return not msg & self.api.MNodeMessage.kAttributeLocked
        self.aliases['attribute.lock.set'] = (attributeChange, unregMsg, attributeLockSetIntercept)

        def attributeLockUnsetIntercept(msg, plug, otherPlug, clientData):
            return not msg & self.api.MNodeMessage.kAttributeUnlocked
        self.aliases['attribute.lock.unset'] = (attributeChange, unregMsg, attributeLockUnsetIntercept)

        def attributeKeyableChangeIntercept(msg, plug, otherPlug, clientData):
            return not msg & (self.api.MNodeMessage.kAttributeKeyable | self.api.MNodeMessage.kAttributeUnkeyable)
        self.aliases['attribute.keyable.changed'] = (attributeChange, unregMsg, attributeKeyableChangeIntercept)

        def attributeKeyableSetIntercept(msg, plug, otherPlug, clientData):
            return not msg & self.api.MNodeMessage.kAttributeKeyable
        self.aliases['attribute.keyable.set'] = (attributeChange, unregMsg, attributeKeyableSetIntercept)

        def attributeKeyableUnsetIntercept(msg, plug, otherPlug, clientData):
            return not msg & self.api.MNodeMessage.kAttributeUnkeyable
        self.aliases['attribute.keyable.unset'] = (attributeChange, unregMsg, attributeKeyableUnsetIntercept)

        def attributeKeyableOverride(func, plug, clientData=None):
            return om2.MNodeMessage.addKeyableChangeOverride(plug, func, clientData)
        self.aliases['attribute.keyable.override'] = (attributeKeyableOverride, unregMsg)

        def attributeNameChangeIntercept(msg, plug, otherPlug, clientData):
            return not msg & self.api.MNodeMessage.kAttributeRenamed
        self.aliases['attribute.name.changed'] = (attributeChange, unregMsg, attributeNameChangeIntercept)

        def undo(func, clientData=None):
            return self.api.MEventMessage.addEventCallback('undo', func, clientData)
        self.aliases['undo'] = (undo, unregMsg)

        def redo(func, clientData=None):
            return self.api.MEventMessage.addEventCallback('redo', func, clientData)
        self.aliases['redo'] = (redo, unregMsg)

        def selectionChangeBefore(func, clientData=None):
            return self.api.MEventMessage.addEventCallback('PreSelectionChangedTriggered', func, clientData)
        self.aliases['selection.changed.before'] = (selectionChangeBefore, unregMsg)

        def selectionChangeAfter(func, clientData=None):
            return self.api.MEventMessage.addEventCallback('SelectionChanged', func, clientData)
        self.aliases['selection.changed'] = self.aliases['selection.changed.after'] = (selectionChangeAfter, unregMsg)

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
        register = partial(self.api.MSceneMessage.addCallback, msg)
        unregister = self.api.MSceneMessage.removeCallback
        callback = CallbackProxy(func.__name__, register, unregister,
                                 func, (), {'clientData': clientData}).register()
        self._callbacks.append(callback)
        return callback

    def addSceneCheckMessage(self, msg, func, clientData=None):
        """Add a scene callback.

        Parameters:
            msg (int): Scene check message.
                kBeforeNewCheck
                kBeforeImportCheck
                kBeforeOpenCheck
                kBeforeExportCheck
                kBeforeSaveCheck
                kBeforeCreateReferenceCheck
                kBeforeLoadReferenceCheck

            func (callable): Callback function.
                Signature: (clientData: Any) -> bool

            clientData (any): Data to pass to the callback.
        """
        register = partial(self.api.MSceneMessage.addCheckCallback, msg)
        unregister = self.api.MSceneMessage.removeCallback
        callback = CallbackProxy(func.__name__, register, unregister,
                                 func, (), {'clientData': clientData}).register()
        self._callbacks.append(callback)
        return callback

    def addSceneFileCheckMessage(self, msg, func, clientData=None):
        """Add a scene file check callback.

        Parameters:
            msg (int): Scene file check message.
                kBeforeImportCheck
                kBeforeOpenCheck
                kBeforeExportCheck
                kBeforeCreateReferenceCheck
                kBeforeLoadReferenceCheck

            func (callable): Callback function.
                Signature: (file: MFileObject, clientData: Any) -> bool

            clientData (any): Data to pass to the callback.
        """
        register = partial(self.api.MSceneMessage.addCheckFileCallback, msg)
        unregister = self.api.MSceneMessage.removeCallback
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
        register = partial(self.api.MSceneMessage.addStringArrayCallback, msg)
        unregister = self.api.MSceneMessage.removeCallback
        callback = CallbackProxy(func.__name__, register, unregister,
                                 func, (), {'clientData': clientData}).register()
        self._callbacks.append(callback)
        return callback

    def addEventMessage(self, event, func, clientData=None):
        """Add an event callback.

        Parameters:
            event (str): Name of the event.
                View all events with `MEventMessage.getEventNames()`.

            func (callable): Callback function.
                Signature: (clientData: Any) -> None

            clientData (any): Data to pass to the callback.
        """
        register = partial(self.api.MEventMessage.addEventCallback, event)
        unregister = self.api.MMessage.removeCallback
        callback = CallbackProxy(func.__name__, register, unregister,
                                 func, (), {'clientData': clientData}).register()
        self._callbacks.append(callback)
        return callback

    def addConditionMessage(self, condition, func, clientData=None):
        """Add a condition change callback.

        Parameters:
            condition (str): Name of the condition.
                View all conditions with `MConditionMessage.getConditionNames()`.

            func (callable): Callback function.
                Signature: (clientData: Any) -> None

            clientData (any): Data to pass to the callback.
        """
        register = partial(self.api.MConditionMessage.addConditionCallback, condition)
        unregister = self.api.MMessage.removeCallback
        callback = CallbackProxy(func.__name__, register, unregister,
                                 func, (), {'clientData': clientData}).register()
        self._callbacks.append(callback)
        return callback

    def addMessage(self, register, func, *args, **kwargs):
        """Add a message callback.

        Parameters:
            register (callable): Function to add a callback.
                Must be an instance of `MMessage` and return an ID.
                Classes like `MNodeMessage` and `MDGMessage` can be run
                through this.

            func (callable): Callback function.
                Signature: (clientData: Any) -> None

            args/kwargs: Extra data to pass after the function.
                If anything needs to be passed before the function, such
                as a node, then use `partial(register, node)` as the
                registry function.
        """
        unregister = self.api.MMessage.removeCallback
        callback = CallbackProxy(func.__name__, register, unregister,
                                 func, args, kwargs).register()
        self._callbacks.append(callback)
        return callback

    def addScriptJobEvent(self, event, func):
        """Add a new scriptJob event callback.

        Parameters:
            event (str): Name of the event.
                View all events with `mc.scriptJob(listEvents=True)`.

            func (callable): Callback function.
                Signature: () -> None
        """
        register = lambda func, *args, **kwargs: mc.scriptJob(event=[event, func], *args, **kwargs)
        unregister = lambda callbackID: mc.scriptJob(kill=callbackID) if mc.scriptJob(exists=callbackID) else None
        callback = CallbackProxy(func.__name__, register, unregister, func, (), {}).register()
        self._callbacks.append(callback)
        return callback

    def addScriptJobCondition(self, condition, func):
        """Add a new scriptJob condition change callback.

        Parameters:
            condition (str): Name of the condition.
                View all conditions with `mc.scriptJob(listConditions=True)`.

            func (callable): Callback function.
                Signature: () -> None
        """
        register = lambda func, *args, **kwargs: mc.scriptJob(conditionChange=[condition, func], *args, **kwargs)
        unregister = lambda callbackID: mc.scriptJob(kill=callbackID) if mc.scriptJob(exists=callbackID) else None
        callback = CallbackProxy(func.__name__, register, unregister, func, (), {}).register()
        self._callbacks.append(callback)
        return callback
