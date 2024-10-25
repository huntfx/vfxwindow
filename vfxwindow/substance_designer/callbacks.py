from __future__ import absolute_import

import sd

from ..abstract.callbacks import AbstractCallbacks


class SubstanceDesignerCallbacks(AbstractCallbacks):
    """Substance Designer callbacks.

    Callbacks:
        file.load.before:
            Called before when a file is loaded.
            Signature: (filePath: str) -> None

        file.load.after:
            Called after a file is loaded.
            Signature: (filePath: str, succeed: bool, updated: bool) -> None

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

        ui.graph.add:
            Called when a new graphView is created.
            Signature (graphViewID: int) -> None

        ui.explorer.add:
            Called when a new explorer panel is created.
            Signature (explorerID: int) -> None

        ui.explorer.selection.changed:
            Called when the selection in the explorer panel changes.
            Signature (explorerID: int) -> None
    """

    def _setupAliases(self):
        """Setup Substance Designer callback aliases."""
        app = sd.getContext().getSDApplication()
        manager = app .getQtForPythonUIMgr()

        self.aliases['file.load.before'] = (app.registerBeforeFileLoadedCallback, app.unregisterCallback)
        self.aliases['file.load'] = self.aliases['file.load.after'] = (app.registerAfterFileLoadedCallback, app.unregisterCallback)
        self.aliases['file.save.before'] = (app.registerBeforeFileSavedCallback, app.unregisterCallback)
        self.aliases['file.save'] = self.aliases['file.save.after'] = (app.registerAfterFileSavedCallback, app.unregisterCallback)
        self.aliases['file.close.before'] = (app.registerBeforeFileClosedCallback, app.unregisterCallback)
        self.aliases['file.close'] = self.aliases['file.close.after'] = (app.registerAfterFileClosedCallback, app.unregisterCallback)
        self.aliases['ui.graph.add'] = (manager.registerGraphViewCreatedCallback, manager.unregisterCallback)
        self.aliases['ui.explorer.add'] = (manager.registerExplorerCreatedCallback, manager.unregisterCallback)
        self.aliases['ui.explorer.selection.changed'] = (manager.registerExplorerSelectionChangedCallback, manager.unregisterCallback)

    @property
    def registerAvailable(self):
        """Only register if the GUI is loaded."""
        return self.gui is not None and not self.gui._isHiddenSD
