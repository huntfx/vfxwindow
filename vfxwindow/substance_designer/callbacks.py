from __future__ import absolute_import

from functools import partial

import sd

from ..abstract.callbacks import AbstractCallbacks, CallbackProxy


APPLICATION = sd.getContext().getSDApplication()

MANAGER = APPLICATION.getQtForPythonUIMgr()


class SubstanceDesignerCallbacks(AbstractCallbacks):
    def add(self, name, func, *args, **kwargs):
        """Register a callback.

        Callbacks:
            file.load.before:
                Called before when a file is loaded.
                Signature: (filePath: str) -> None

            file.load.after:
                Called after a file is loaded.
                Signature: (filePath: str, succeed: bool, updated, bool) -> None

            file.save.before:
                Called before when a file is saved.
                Signature: (filePath: str, parentPackagePath: str) -> None

            file.save.after:
                Called after when a file is saved.
                Signature: (filePath: str, succeed: bool) -> None

            file.close.before:
                Called before a file is closed.
                Signature: (filePath: str) -> None

            file.close.after:
                Called after a file is saved.
                Signature: (filePath: str, succeed: bool) -> None

            ui.graph.created:
                Called when a new graphView is created.
                Signature (graphViewID: int) -> None

            ui.explorer.created:
                Called when a new explorer panel is created.
                Signature (explorerID: int) -> None

            ui.explorer.selection.changed:
                Called when the selection in the explorer panel changes.
                Signature (explorerID: int) -> None
        """
        parts = name.split('.') + [None, None, None]

        register = unregister = None
        if parts[0] == 'file':
            unregister = APPLICATION.unregisterCallback
            if parts[1] == 'load':
                if parts[2] == 'before':
                    register = APPLICATION.registerBeforeFileLoadedCallback
                elif parts[2] in ('after', None):
                    register = APPLICATION.registerAfterFileLoadedCallback
            elif parts[1] == 'save':
                if parts[2] == 'before':
                    register = APPLICATION.registerBeforeFileSavedCallback
                elif parts[2] in ('after', None):
                    register = APPLICATION.registerAfterFileSavedCallback
            elif parts[1] == 'close':
                if parts[2] == 'before':
                    register = APPLICATION.registerAfterFileClosedCallback
                elif parts[2] in ('after', None):
                    register = APPLICATION.registerBeforeFileClosedCallback

        elif parts[0] == 'ui':
            unregister = MANAGER.unregisterCallback
            if parts[1] == 'graph':
                if parts[2] == 'created':
                    register = MANAGER.registerGraphViewCreatedCallback
            elif parts[1] == 'explorer':
                if parts[2] == 'created':
                    register = MANAGER.registerExplorerCreatedCallback
                elif parts[2] == 'selection':
                    if parts[3] == 'changed':
                        register = MANAGER.registerExplorerSelectionChangedCallback

        if register is None:
            return None

        callback = CallbackProxy(name, register, unregister, func, args, kwargs)

        # Only register if the Nuke window is loaded
        # TODO: Test what happens when a group is unloaded in Substance Designer
        if self.gui is not None and not self.gui._isHiddenSD:
            callback.register()

        self._callbacks.append(callback)
        return callback
