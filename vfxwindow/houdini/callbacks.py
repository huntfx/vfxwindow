from __future__ import absolute_import

import hou

from ..abstract.callbacks import AbstractCallbacks, CallbackProxy


class HoudiniCallbackProxy(CallbackProxy):

    def forceUnregister(self):
        self.alias.unregister(self.func, *self._args, **self._kwargs)


class HoudiniCallbacks(AbstractCallbacks):
    """Houdini callbacks.
    Each of these callbacks receives their parameters as keyword
    arguments, and an optional `None` should be treated as if the
    parameter is not passed in.

    Callbacks:
        file:
            Called for any file events.
            Parameters: ()
            Signature: (event_type: hou.hipFileEventType) -> None

        file.clear:
            Mapped to 'file.clear.after'

        file.clear.before:
            Called before the current .hip file is cleared.
            For example during a "File > New" operation.
            Parameters: ()
            Signature: (event_type: hou.hipFileEventType.BeforeClear) -> None

        file.clear.after:
            Called after the current .hip file is cleared.
            For example during a "File > New" operation.
            Parameters: ()
            Signature: (event_type: hou.hipFileEventType.AfterClear) -> None

        file.load:
            Mapped to 'file.load.after'

        file.load.before:
            Called before a .hip file is loaded into Houdini.
            Parameters: ()
            Signature: (event_type: hou.hipFileEventType.BeforeLoad) -> None

        file.load.after:
            Called after a .hip file is loaded into Houdini.
            Parameters: ()
            Signature: (event_type: hou.hipFileEventType.AfterLoad) -> None

        file.merge:
            Mapped to 'file.merge.after'

        file.merge.before:
            Called before a .hip file is merged into the current Houdini session.
            Parameters: ()
            Signature: (event_type: hou.hipFileEventType.BeforeMerge) -> None

        file.merge.after:
            Called after a .hip file is merged into the current Houdini session.
            Parameters: ()
            Signature: (event_type: hou.hipFileEventType.AfterMerge) -> None

        file.save:
            Mapped to 'file.save.after'

        file.save.before:
            Called before the current .hip file is saved.
            Parameters: ()
            Signature: (event_type: hou.hipFileEventType.BeforeSave) -> None

        file.save.after:
            Called after the current .hip file is saved.
            Parameters: ()
            Signature: (event_type: hou.hipFileEventType.AfterSave) -> None

        playbar:
            Called whenever a playbar event occurs.
            Parameters: ()
            Signature: (event_type: hou.playbarEvent, frame: int) -> None

        playback:
            Called when playback is started or stopped.
            Parameters: ()
            Signature: (event_type: hou.playbarEvent, frame: int) -> None

        playback.start:
            Called when playback is started either in the forward or
            reverse direction.
            Parameters: ()
            Signature: (event_type: hou.playbarEvent, frame: int) -> None

        playback.stop:
            Called when playback is stopped.
            Parameters: ()
            Signature: (event_type: hou.playbarEvent, frame: int) -> None

        frame.changed:
            Called after the current frame has changed when the scene
            has been cooked for the new frame.
            Parameters: ()
            Signature: (event_type: hou.playbarEvent, frame: int) -> None

        asset.create:
            Called when a new asset is created.
            Parameters: ()
            Signature: (event_type: hou.hdaEventType, asset_definition: hou.HDADefinition) -> None

        asset.remove:
            Called after an asset is deleted.
            Parameters: ()
            Signature: (event_type: hou.hdaEventType, asset_name: str, library_path: str,
                        node_type_category: hou.NodeTypeCategory) -> None

        asset.save:
            Called when an asset is saved.
            Parameters: ()
            Signature: (event_type: hou.hdaEventType, asset_definition: hou.HDADefinition) -> None

        asset.library.install:
            Called when a digital asset library is installed into the
            current session.
            Parameters: ()
            Signature: (event_type: hou.hdaEventType, library_path: str) -> None

        asset.library.uninstall:
            Called when a digital asset library is uninstalled from
            the current session.
            Parameters: ()
            Signature: (event_type: hou.hdaEventType, library_path: str) -> None

        node.selection.changed:
            Called after the selection associated with the node changes.
            Parameters: (node: hou.Node | str)
            Signature: (node: hou.Node, event_type: hou.nodeEventType) -> None

        node.remove:
            Called before a node is deleted.
            You cannot cancel the deletion.
            Parameters: (node: hou.Node | str)
            Signature: (node: hou.Node, event_type: hou.nodeEventType) -> None

        node.name.changed:
            Called after a node is renamed.
            Get the new name using `hou.Node.name`.
            Parameters: (node: hou.Node | str)
            Signature: (node: hou.Node, event_type: hou.nodeEventType) -> None

        node.flag.changed:
            Called after one of the node flags are turned on or off.
            Parameters: (node: hou.Node | str)
            Signature: (node: hou.Node, event_type: hou.nodeEventType) -> None

        node.appearance.changed:
            Called after an event that changes what the node looks like
            in the network editor.
            Parameters: (node: hou.Node | str)
            Signature: (node: hou.Node, event_type: hou.nodeEventType, change_type: hou.appearanceChangeType) -> None

        node.position.changed:
            Called after the node is moved in the network editor.
            Get the new position using `hou.Node.position`.
            Parameters: (node: hou.Node | str)
            Signature: (node: hou.Node, event_type: hou.nodeEventType) -> None

        node.input.changed:
            Called when a node input is connected or disconnected.
            Parameters: (node: hou.Node | str)
            Signature: (node: hou.Node, event_type: hou.nodeEventType, input_index: int) -> None

        node.parameter.changed:
            Called after a parameter value changes.
            Get the new value using `hou.ParamTuple.eval`.
            If multiple parameters change, the callback will only
            trigger once with `param_tuple` set to `None`.
            Parameters: (node: hou.Node | str)
            Signature: (node: hou.Node, event_type: hou.nodeEventType, param_tuple: hou.ParmTuple | None) -> None

        node.parameter.spare.changed:
            Called after a spare parameter is modified on, added to,
            or removed from the node.
            If the node has spare parameters, then this event triggers
            when any parameter is modified, not just spare parameters.
            Parameters: (node: hou.Node | str)
            Signature: (node: hou.Node, event_type: hou.nodeEventType) -> None

        node.child.create:
            Called when a new node is created inside a subnet node.
            Parameters: (node: hou.Node | str)
            Signature: (node: hou.Node, event_type: hou.nodeEventType, child_node: hou.Node) -> None

        node.child.remove:
            Called before a node is deleted inside a subnet node.
            Parameters: (node: hou.Node | str)
            Signature: (node: hou.Node, event_type: hou.nodeEventType, child_node: hou.Node) -> None

        node.child.changed:
            Called when the current node, display flag, or render flag
            is changed inside a subnet node.
            Parameters: (node: hou.Node | str)
            Signature: (node: hou.Node, event_type: hou.nodeEventType, child_node: hou.Node | None) -> None

        node.child.selection.changed:
            Called when a node selection is changed inside a subnet node.
            Get the new selection with `hou.Node.selectedChildren`.
            Parameters: (node: hou.Node | str)
            Signature: (node: hou.Node, event_type: hou.nodeEventType) -> None

        viewport.camera.changed:
            Called when the viewport camera has been changed.
            Parameters: (viewport: hou.GeometryViewport)
            Signature: (event_type: hou.geometryViewportEvent, desktop: hou.Desktop,
                        viewer: hou.SceneViewer, viewport: hou.GeometryViewport) -> None
    """

    CallbackProxy = HoudiniCallbackProxy

    def _setupAliases(self):
        """Setup Houdini callback aliases."""
        def hfReg(func): hou.hipFile.addEventCallback(func)
        def hfUnreg(func): hou.hipFile.removeEventCallback(func)
        def hfIntercept(*event_types):
            def hfIntercept(event_type): return event_type not in event_types
            return hfIntercept
        def hfCheck(func): return func in hou.hipFile.eventCallbacks()
        self.aliases['file'] = (hfReg, hfUnreg, None, hfCheck)
        self.aliases['file.clear.before'] = (hfReg, hfUnreg, hfIntercept(hou.hipFileEventType.BeforeClear), hfCheck)
        self.aliases['file.clear'] =  self.aliases['file.clear.after'] = (hfReg, hfUnreg, hfIntercept(hou.hipFileEventType.AfterClear), hfCheck)
        self.aliases['file.load.before'] = (hfReg, hfUnreg, hfIntercept(hou.hipFileEventType.BeforeLoad), hfCheck)
        self.aliases['file.load'] =  self.aliases['file.load.after'] = (hfReg, hfUnreg, hfIntercept(hou.hipFileEventType.AfterLoad), hfCheck)
        self.aliases['file.merge.before'] = (hfReg, hfUnreg, hfIntercept(hou.hipFileEventType.BeforeMerge), hfCheck)
        self.aliases['file.merge'] =  self.aliases['file.merge.after'] = (hfReg, hfUnreg, hfIntercept(hou.hipFileEventType.AfterMerge), hfCheck)
        self.aliases['file.save.before'] = (hfReg, hfUnreg, hfIntercept(hou.hipFileEventType.BeforeSave), hfCheck)
        self.aliases['file.save'] =  self.aliases['file.save.after'] = (hfReg, hfUnreg, hfIntercept(hou.hipFileEventType.AfterSave), hfCheck)

        def pbReg(func): hou.playbar.addEventCallback(func)
        def pbUnreg(func): hou.playbar.removeEventCallback(func)
        def pbIntercept(*event_types):
            def pbIntercept(event_type, frame): return event_type not in event_types
            return pbIntercept
        def pbCheck(func): return func in hou.playbar.eventCallbacks()
        self.aliases['playbar'] = (pbReg, pbUnreg, None, pbCheck)
        self.aliases['playback'] = (pbReg, pbUnreg, pbIntercept(hou.playbarEvent.Started, hou.playbarEvent.Stopped), pbCheck)
        self.aliases['playback.start'] = (pbReg, pbUnreg, pbIntercept(hou.playbarEvent.Started), pbCheck)
        self.aliases['playback.stop'] = (pbReg, pbUnreg, pbIntercept(hou.playbarEvent.Stopped), pbCheck)
        self.aliases['frame.changed'] = (pbReg, pbUnreg, pbIntercept(hou.playbarEvent.FrameChanged), pbCheck)

        def hdaReg(event_type):
            def hdaReg(func): hou.hda.addEventCallback((event_type,), func)
            return hdaReg
        def hdaUnreg(event_type):
            def hdaUnreg(func): hou.hda.removeEventCallback((event_type,), func)
            return hdaUnreg
        def hdaCheck(event_type):
            def hdaCheck(func): return ((event_type,), func) in hou.hda.eventCallbacks()
            return hdaCheck
        hdaEvents = {
            'asset.create': hou.hdaEventType.AssetCreated,
            'asset.remove': hou.hdaEventType.AssetDeleted,
            'asset.save': hou.hdaEventType.AssetSaved,
            'asset.library.install': hou.hdaEventType.LibraryInstalled,
            'asset.library.uninstall': hou.hdaEventType.LibraryUninstalled,
        }
        for alias, event in hdaEvents.items():
            self.aliases[alias] = (hdaReg(event), hdaUnreg(event), None, hdaCheck(event))

        def _getNode(node):
            if isinstance(node, hou.Node): return node
            node, name = hou.node(node), node
            if node is not None: return node
            raise ValueError('"{}" is not a valid node'.format(name))
        def ndReg(event_type):
            def ndReg(func, node): _getNode(node).addEventCallback((event_type,), func)
            return ndReg
        def ndUnreg(event_type):
            def ndUnreg(func, node):
                try:  _getNode(node).removeEventCallback((event_type,), func)
                except (ValueError, hou.ObjectWasDeleted): pass
            return ndUnreg
        def ndCheck(event_type):
            def ndCheck(func, node):
                try: return ((event_type,), func) in _getNode(node).eventCallbacks()
                except (ValueError, hou.ObjectWasDeleted): return False
            return ndCheck
        nodeEvents = {
            'node.remove': hou.nodeEventType.BeingDeleted,
            'node.name.changed': hou.nodeEventType.NameChanged,
            'node.flag.changed': hou.nodeEventType.FlagChanged,
            'node.appearance.changed': hou.nodeEventType.AppearanceChanged,
            'node.position.changed': hou.nodeEventType.PositionChanged,
            'node.input.changed': hou.nodeEventType.InputRewired,
            'node.parameter.changed': hou.nodeEventType.ParmTupleChanged,
            'node.parameter.spare.changed': hou.nodeEventType.SpareParmTemplatesChanged,
            'node.child.create': hou.nodeEventType.ChildCreated,
            'node.child.remove': hou.nodeEventType.ChildDeleted,
            'node.child.changed': hou.nodeEventType.ChildSwitched,
            'node.child.selection.changed': hou.nodeEventType.ChildSelectionChanged,
            'node.selection.changed': hou.nodeEventType.SelectionChanged
        }
        for alias, event in nodeEvents.items():
            self.aliases[alias] = (ndReg(event), ndUnreg(event), None, ndCheck(event))

        def gvReg(func, geometryViewport): geometryViewport.addEventCallback(func)
        def gvUnreg(func, geometryViewport): geometryViewport.removeEventCallback(func)
        def gvIntercept(*event_types):
            def gvIntercept(event_type, desktop, viewer, viewport): return event_type not in event_types
            return gvIntercept
        def gvCheck(func, geometryViewport): return func in geometryViewport.eventCallbacks()
        self.aliases['viewport.camera.changed'] = (gvReg, gvUnreg, gvIntercept(hou.geometryViewportEvent.CameraSwitched), gvCheck)
