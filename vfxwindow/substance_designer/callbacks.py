from __future__ import absolute_import

import sd

from ..abstract.callbacks import AbstractCallbacks, CallbackProxy


class SubstanceDesignerCallbackProxy(CallbackProxy):
    @property
    def registered(self):
        """Determine if the callback is registered.

        There is no obvious way of doing this, but digging into the
        code reveals a callback map that contains a dict of callback IDs
        to their corresponding C functions. The ID only increments so it
        should be safe enough, but I obviously can't trust this to not
        change, so it's also wrapped in a try/except.
        """
        if self._result is None:
            return False
        try:
            return self._result in sd.api.sdcallbackmap.SDCallbackMap._SDCallbackMap__mCallbacksMap
        except AttributeError:
            return super(SubstanceDesignerCallbackProxy, self).registered



class SubstanceDesignerCallbacks(AbstractCallbacks):
    """Substance Designer callbacks.

    Callbacks:
        file.load:
            Mapped to 'file.load.after'.

        file.load.before:
            Called before a file is loaded.
            Signature: (filePath: bytes) -> None

        file.load.after:
            Called after a file is loaded.
            Signature: (filePath: bytes, succeed: bool, updated: bool) -> None

        file.save:
            Mapped to 'file.save.after'.

        file.save.before:
            Called before a file is saved.
            Signature: (filePath: bytes, parentPackagePath: bytes) -> None

        file.save.after:
            Called after a file is saved.
            Signature: (filePath: bytes, succeed: bool) -> None

        file.close:
            Mapped to 'file.close.after'.

        file.close.before:
            Called before a file is closed.
            Signature: (filePath: bytes) -> None

        file.close.after:
            Called after a file is closed.
            Signature: (filePath: bytes, succeed: bool) -> None

        ui.graph.create:
            Called when a new graphView is created.
            Signature: (graphViewID: int) -> None

        ui.explorer.create:
            Called when a new explorer panel is created.
            Signature: (explorerID: int) -> None

        ui.explorer.selection.changed:
            Called when the selection in the explorer panel changes.
            Signature: (explorerID: int) -> None
    """

    CallbackProxy = SubstanceDesignerCallbackProxy

    def _setupAliases(self):
        """Setup Substance Designer callback aliases."""
        app = sd.getContext().getSDApplication()
        manager = app.getQtForPythonUIMgr()

        self.aliases['file.load.before'] = (app.registerBeforeFileLoadedCallback, app.unregisterCallback)
        self.aliases['file.load'] = self.aliases['file.load.after'] = (app.registerAfterFileLoadedCallback, app.unregisterCallback)
        self.aliases['file.save.before'] = (app.registerBeforeFileSavedCallback, app.unregisterCallback)
        self.aliases['file.save'] = self.aliases['file.save.after'] = (app.registerAfterFileSavedCallback, app.unregisterCallback)
        self.aliases['file.close.before'] = (app.registerBeforeFileClosedCallback, app.unregisterCallback)
        self.aliases['file.close'] = self.aliases['file.close.after'] = (app.registerAfterFileClosedCallback, app.unregisterCallback)
        self.aliases['ui.graph.create'] = (manager.registerGraphViewCreatedCallback, manager.unregisterCallback)
        self.aliases['ui.explorer.create'] = (manager.registerExplorerCreatedCallback, manager.unregisterCallback)
        self.aliases['ui.explorer.selection.changed'] = (manager.registerExplorerSelectionChangedCallback, manager.unregisterCallback)

    @property
    def registerAvailable(self):
        """Only register if the GUI is loaded."""
        return self.gui is not None and not self.gui._isHiddenSD
