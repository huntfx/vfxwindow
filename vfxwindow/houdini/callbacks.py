from __future__ import absolute_import

from functools import partial

import hou

from ..abstract.callbacks import AbstractCallbacks, CallbackProxy


class HoudiniCallbackProxy(CallbackProxy):

    def forceUnregister(self):
        self._unregister(self.func)

    @property
    def registered(self):
        """Determine if the callback is registered."""
        if self._register is hou.hipFile.addEventCallback:
            return self.func in hou.fipFile.eventCallbacks()
        return super(HoudiniCallbackProxy, self).registered


class HoudiniCallbacks(AbstractCallbacks):
    """Houdini callbacks.

    Callbacks:
        file:
            Called for any file events.
            Signature: (event_type: hou.hipFileEventType) -> None

        file.clear:
            Mapped to 'file.clear.after'

        file.clear.before:
            Called before before the current .hip file is cleared.
            For example during a "File > New" operation.
            Signature: (event_type: hou.hipFileEventType.BeforeClear) -> None

        file.clear.after:
            Called after a after the current .hip file is cleared.
            For example during a "File > New" operation.
            Signature: (event_type: hou.hipFileEventType.AfterClear) -> None

        file.load.before:
            Called before a .hip file is loaded into Houdini.
            Signature: (event_type: hou.hipFileEventType.BeforeLoad) -> None

        file.load.after:
            Called after a .hip file is loaded into Houdini.
            Signature: (event_type: hou.hipFileEventType.AfterLoad) -> None

        file.merge.before:
            Called before a .hip file is merged into the current Houdini session.
            Signature: (event_type: hou.hipFileEventType.BeforeMerge) -> None

        file.merge.after:
            Called after a .hip file is merged into the current Houdini session.
            Signature: (event_type: hou.hipFileEventType.AfterMerge) -> None

        file.save.before:
            Called before the current .hip file is saved.
            Signature: (event_type: hou.hipFileEventType.BeforeSave) -> None

        file.save.after:
            Called after the current .hip file is saved.
            Signature: (event_type: hou.hipFileEventType.AfterSave) -> None

        playbar:
            Called whenever a playbar event occurs.
            Signature: (event_type: hou.playbarEvent, frame: int) -> None

        playback:
            Called when playback is started or stopped.
            Signature: (event_type: hou.playbarEvent, frame: int) -> None

        playback.start:
            Called when playback is started either in the forward or
            reverse direction.
            Signature: (event_type: hou.playbarEvent, frame: int) -> None

        playback.stop:
            Called when playback is stopped.
            Signature: (event_type: hou.playbarEvent, frame: int) -> None

        frame.changed:
            Called after the current frame has changed when the scene
            has been cooked for the new frame.
            Signature: (event_type: hou.playbarEvent, frame: int) -> None

        asset.create:
            Called when a new asset is created.
            Signature: (event_type: hou.hdaEventType, asset_definition: hou.HDADefinition) -> None

        asset.remove:
            Called after an asset is deleted.
            Signature: (event_type: hou.hdaEventType, asset_name: str, library_path: str,
                        node_type_category: hou.NodeTypeCategory) -> None

        asset.save:
            Called when an asset is saved.
            Signature: (event_type: hou.hdaEventType, asset_definition: hou.HDADefinition) -> None

        asset.library.install:
            Called when a digital asset library is installed into the
            current session.
            Signature: (event_type: hou.hdaEventType, library_path: str) -> None

        asset.library.uninstall:
            Called when a digital asset library is uninstalled from
            the current ession.
            Signature: (event_type: hou.hdaEventType, library_path: str) -> None
    """

    CallbackProxy = HoudiniCallbackProxy

    def _setupAliases(self):
        """Setup Houdini callback aliases."""
        hfReg = hou.hipFile.addEventCallback
        hfUnreg = hou.hipFile.removeEventCallback
        hfE = hou.hipFileEventType
        self.aliases['file'] = (hfReg, hfUnreg)
        self.aliases['file.clear.before'] = (hfReg, hfUnreg, lambda e: e != hfE.BeforeClear)
        self.aliases['file.clear'] =  self.aliases['file.clear.after'] = (hfReg, hfUnreg, lambda e: e != hfE.AfterClear)
        self.aliases['file.load.before'] = (hfReg, hfUnreg, lambda e: e != hfE.BeforeLoad)
        self.aliases['file.load'] =  self.aliases['file.load.after'] = (hfReg, hfUnreg, lambda e: e != hfE.AfterLoad)
        self.aliases['file.merge.before'] = (hfReg, hfUnreg, lambda e: e != hfE.BeforeMerge)
        self.aliases['file.merge'] =  self.aliases['file.merge.after'] = (hfReg, hfUnreg, lambda e: e != hfE.AfterMerge)
        self.aliases['file.save.before'] = (hfReg, hfUnreg, lambda e: e != hfE.BeforeSave)
        self.aliases['file.save'] =  self.aliases['file.save.after'] = (hfReg, hfUnreg, lambda e: e != hfE.AfterSave)

        pbReg = hou.playbar.addEventCallback
        pbUnreg = hou.playbar.removeEventCallback
        pbE = hou.playbarEvent
        self.aliases['playbar'] = (pbReg, pbUnreg)
        self.aliases['playback'] = (pbReg, pbUnreg, lambda e, f: e not in (pbE.Started, pbE.Stopped))
        self.aliases['playback.start'] = (pbReg, pbUnreg, lambda e, f: e != pbE.Started)
        self.aliases['playback.stop'] = (pbReg, pbUnreg, lambda e, f: e != pbE.Stopped)
        self.aliases['frame.changed'] = (pbReg, pbUnreg, lambda e, f: e != pbE.FrameChanged)

        hdaReg = lambda event_type: partial(hou.hda.addEventCallback, (event_type,))
        hdaUnreg = hou.hda.removeEventCallback
        hdaE = hou.hdaEventType
        self.aliases['asset.create'] = (hdaReg(hdaE.AssetCreated), hdaUnreg)
        self.aliases['asset.remove'] = (hdaReg(hdaE.AssetDeleted), hdaUnreg)
        self.aliases['asset.save'] = (hdaReg(hdaE.AssetSaved), hdaUnreg)
        self.aliases['asset.library.install'] = (hdaReg(hdaE.LibraryInstalled), hdaUnreg)
        self.aliases['asset.library.uninstall'] = (hdaReg(hdaE.LibraryUninstalled), hdaUnreg)
