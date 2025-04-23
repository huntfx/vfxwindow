from __future__ import absolute_import

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
    """

    CallbackProxy = HoudiniCallbackProxy

    def _setupAliases(self):
        """Setup Houdini callback aliases."""
        hfRef = hou.hipFile.addEventCallback
        hfUnreg = hou.hipFile.removeEventCallback
        hfE = hou.hipFileEventType

        self.aliases['file'] = (hfRef, hfUnreg)
        self.aliases['file.clear.before'] = (hfRef, hfUnreg, lambda e: e != hfE.BeforeClear)
        self.aliases['file.clear'] =  self.aliases['file.clear.after'] = (hfRef, hfUnreg, lambda e: e != hfE.AfterClear)
        self.aliases['file.load.before'] = (hfRef, hfUnreg, lambda e: e != hfE.BeforeLoad)
        self.aliases['file.load'] =  self.aliases['file.load.after'] = (hfRef, hfUnreg, lambda e: e != hfE.AfterLoad)
        self.aliases['file.merge.before'] = (hfRef, hfUnreg, lambda e: e != hfE.BeforeMerge)
        self.aliases['file.merge'] =  self.aliases['file.merge.after'] = (hfRef, hfUnreg, lambda e: e != hfE.AfterMerge)
        self.aliases['file.save.before'] = (hfRef, hfUnreg, lambda e: e != hfE.BeforeSave)
        self.aliases['file.save'] =  self.aliases['file.save.after'] = (hfRef, hfUnreg, lambda e: e != hfE.AfterSave)
