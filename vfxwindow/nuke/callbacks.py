from __future__ import absolute_import

from functools import partial

import nuke

from ..abstract.callbacks import AbstractCallbacks, CallbackProxy


class NukeCallbackProxy(CallbackProxy):

    def forceUnregister(self):
        """Unregister the callback without any extra checks."""
        self._unregister(self.func, *self._args, **self._kwargs)


class NukeCallbacks(AbstractCallbacks):
    """Nuke callbacks.

    Callbacks:
        file.load:
            Called whenever a script is loaded.
            This is run immediately after `onCreate` for the root.
            Signature: () -> None

        file.save:
            Called when the user tries to save a script.
            Signature: () -> None

        file.close:
            This is run immediately before `onDestroy` for the root.
            In GUI mode, if `nuke.root().name()` is 'Root' during the
            execution of this, then it means Nuke is shutting down.
            Signature: () -> None

        node.create:
            Called when any node is created.
            To capture when any new scene is created, add this with
            `nodeClass='Root'`. Note that it will also run before
            opening files as well.
            Parameters: (nodeClass: Optional[str] = None)
            Signature: () -> None

        node.create.user:
            Called when any node is created by the user in the GUI.
            Parameters: (nodeClass: Optional[str] = None)
            Signature: () -> None

        node.remove:
            Called when any node is deleted.
            This includes undo, closing a script or exiting Nuke.
            It is not run for preferences, Python knobs or crashes.
            Parameters: (nodeClass: Optional[str] = None)
            Signature: () -> None

        render:
            Mapped to 'render.after'

        render.before:
            Called prior to starting rendering.
            Any error causes the render to abort.
            Signature: () -> None

        render.after:
            Called after rendering of all frames is finished.
            Any error causes the render to abort.
            Signature: () -> None

        render.frame:
            Mapped to 'render.frame.after'

        render.frame.before:
            Called prior to starting rendering of each frame.
            Any error causes the render to abort.
            Signature: () -> None

        render.frame.after:
            Called after each frame has finished rendering.
            Any error causes the render to abort.
            Signature: () -> None

        render.background:
            Mapped to 'render.background.after'

        render.background.after:
            Called after any background renders.
            Signature: (context={'id': ...}) -> None

        render.background.frame:
            Mapped to 'render.background.frame.after'

        render.background.frame.after:
            Called after each frame of a background render.
            Signature: (context={'id': ..., 'frame': int, numFrames: int, frameProgress: int}) -> None

        knob.changed:
            Called when the user changes the value of any knob.
            Only triggers when the control panel is open.
            Parameters: (nodeClass: Optional[str] = None)
            Signature: () -> None

    Unimplemented:
        autolabel
        filenameFilter
        validateFilename
        autoSaveRestoreFilter
        autoSaveDeleteFilter
        updateUI
    """

    CallbackProxy = NukeCallbackProxy

    def _setupAliases(self):
        """Setup Nuke callback aliases."""
        self.aliases['file.load'] = (nuke.addOnScriptLoad, nuke.removeOnScriptLoad)
        self.aliases['file.save'] = (nuke.addOnScriptSave, nuke.removeOnScriptSave)
        self.aliases['file.close'] = (nuke.addOnScriptClose, nuke.removeOnScriptClose)
        self.aliases['node.create'] = (nuke.addOnCreate, nuke.removeOnCreate)
        self.aliases['node.create.user'] = (nuke.addOnUserCreate, nuke.removeOnUserCreate)
        self.aliases['node.remove'] = (nuke.addOnDestroy, nuke.removeOnDestroy)
        self.aliases['knob.changed'] = (nuke.addKnobChanged, nuke.removeKnobChanged)
        self.aliases['render.before'] = (nuke.addBeforeRender, nuke.removeBeforeRender)
        self.aliases['render'] = self.aliases['render.after'] = (nuke.addAfterRender, nuke.removeAfterRender)
        self.aliases['render.frame.before'] = (nuke.addBeforeFrameRender, nuke.removeBeforeFrameRender)
        self.aliases['render.frame'] = self.aliases['render.frame.after'] = (nuke.addAfterFrameRender, nuke.removeAfterFrameRender)
        self.aliases['render.background'] = self.aliases['render.background.after'] = (nuke.addAfterBackgroundRender, nuke.removeAfterBackgroundRender)
        self.aliases['render.background.frame'] = self.aliases['render.background.frame.after'] = (nuke.addAfterBackgroundFrameRender, nuke.removeAfterBackgroundFrameRender)

    @property
    def registerAvailable(self):
        """Only register if the GUI is loaded."""
        return self.gui is not None and not self.gui._isHiddenNk
