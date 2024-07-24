from __future__ import absolute_import

from functools import partial

import nuke

from ..abstract.callbacks import AbstractCallbacks, CallbackProxy


class NukeCallbackProxy(CallbackProxy):

    def getUnregisterParam(self):
        """Get the parameter to pass to the unregister function."""
        return self.callbackFunc


class NukeCallbacks(AbstractCallbacks):
    def add(self, name, func, *args, **kwargs):
        """Register a callback.

        Callbacks:
            new: Called whenever a new script is made.

            load:
                Called whenever a script is loaded.
                This is run immediately after `onCreate` for the root.

            save:
                Called when the user tries to save a script.

            close:
                This is run immediately before `onDestroy` for the root

            create:
                Called when any node is created.
                Examples are loading a script, pasting a node, selecting
                a menu item or undoing a delete.

            destroy:
                Called when any node is deleted.
                This includes undo, closing a script or exiting Nuke.
                It is not run for preferences, Python knobs or crashes.

            render:
                Mapped to 'render.after'

            render.before:
                Called prior to starting rendering.
                Any error causes the render to abort.

            render.after:
                Called after rendering of all frames is finished.
                Any error causes the render to abort.

            render.frame:
                Mapped to 'render.frame.after'

            render.frame.before:
                Called prior to starting rendering of each frame.
                Any error causes the render to abort.

            render.frame.after:
                Called after each frame has finished rendering.
                Any error causes the render to abort.

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

        Unimplemented:
            knobChanged
            updateUI
            autolabel
            filenameFilter
            validateFilename
            autoSaveRestoreFilter
            autoSaveDeleteFilter
        """
        parts = name.split('.') + [None, None, None]

        register = unregister = intercept = None
        if parts[0] == 'new':
            register = partial(nuke.addOnCreate, nodeClass='Root')
            unregister = partial(nuke.removeOnCreate, nodeClass='Root')
            intercept = lambda *args, **kwargs: bool(nuke.thisNode()['name'].value())

        elif parts[0] == 'load':
            register = nuke.addOnScriptLoad
            unregister = nuke.removeOnScriptLoad

        elif parts[0] == 'save':
            register = nuke.addOnScriptSave
            unregister = nuke.removeOnScriptSave

        elif parts[0] == 'close':
            register = nuke.addOnScriptClose
            unregister = nuke.removeOnScriptClose

        elif parts[0] == 'create':
            if parts[1] == 'user':
                register = nuke.addOnUserCreate
                unregister = nuke.removeOnUserCreate
            elif parts[1] is None:
                register = nuke.addOnCreate
                unregister = nuke.removeOnCreate

        elif parts[0] == 'destroy':
            register = nuke.addOnDestroy
            unregister = nuke.removeOnDestroy

        elif parts[0] == 'render':
            if parts[1] == 'before':
                register = nuke.addBeforeRender
                unregister = nuke.removeBeforeRender
            elif parts[1] in ('after', None):
                register = nuke.addAfterRender
                unregister = nuke.removeAfterRender

            elif parts[1] == 'frame':
                if parts[2] == 'before':
                    register = nuke.addBeforeFrameRender
                    unregister = nuke.removeBeforeFrameRender
                elif parts[2] in ('after', None):
                    register = nuke.addAfterFrameRender
                    unregister = nuke.removeAfterFrameRender

            elif parts[1] == 'background':
                if parts[2] in ('after', None):
                    register = nuke.addAfterBackgroundRender
                    unregister = nuke.removeAfterBackgroundRender

                elif parts[2] == 'frame':
                    if parts[3] in ('after', None):
                        register = nuke.addAfterBackgroundFrameRender
                        unregister = nuke.removeAfterBackgroundFrameRender

        if register is None:
            return None

        callback = NukeCallbackProxy(name, register, unregister, func, args, kwargs, intercept)

        # Only register if the Nuke window is loaded
        if self.gui is not None and not self.gui._isHiddenNk:
            callback.register()

        self._callbacks.append(callback)
        return callback
