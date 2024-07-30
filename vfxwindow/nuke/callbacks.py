from __future__ import absolute_import

from functools import partial

import nuke

from ..abstract.callbacks import AbstractCallbacks, CallbackProxy


class NukeCallbackProxy(CallbackProxy):

    def getUnregisterParam(self):
        """Get the parameter to pass to the unregister function."""
        return self.func


class NukeCallbacks(AbstractCallbacks):
    def add(self, name, func, *args, **kwargs):
        """Register a callback.

        Callbacks:
            file.new: Called whenever a new script is made.
                Signature: () -> None

            file.load:
                Called whenever a script is loaded.
                This is run immediately after `onCreate` for the root.
                Signature: () -> None

            file.save:
                Called when the user tries to save a script.
                Signature: () -> None

            file.close:
                This is run immediately before `onDestroy` for the root.
                Signature: () -> None

            node.added:
                Called when any node is created.
                Parameters: (nodeClass: Optional[str] = None)
                Signature: () -> None

            node.added.user:
                Called when any node is created by the user in the GUI.
                Parameters: (nodeClass: Optional[str] = None)
                Signature: () -> None

            node.removed:
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

            ui.update:
                Called when any changes are made to each node.
                This is low priority so Nuke may have already started
                calculating the Viewer image.
                Parameters: (nodeClass: Optional[str] = None)
                Signature: () -> None

        Unimplemented:
            autolabel
            filenameFilter
            validateFilename
            autoSaveRestoreFilter
            autoSaveDeleteFilter
        """
        parts = name.split('.') + [None, None, None]

        register = unregister = intercept = None
        if parts[0] == 'file':
            if parts[1] == 'new':
                register = partial(nuke.addOnCreate, nodeClass='Root')
                unregister = partial(nuke.removeOnCreate, nodeClass='Root')
                intercept = lambda *args, **kwargs: nuke.thisNode().Class() == 'Root'

            elif parts[1] == 'load':
                register = nuke.addOnScriptLoad
                unregister = nuke.removeOnScriptLoad

            elif parts[1] == 'save':
                register = nuke.addOnScriptSave
                unregister = nuke.removeOnScriptSave

            elif parts[1] == 'close':
                register = nuke.addOnScriptClose
                unregister = nuke.removeOnScriptClose

        elif parts[0] == 'node':
            if parts[1] == 'added':
                if parts[2] == 'user':
                    register = nuke.addOnUserCreate
                    unregister = nuke.removeOnUserCreate
                elif parts[2] is None:
                    register = nuke.addOnCreate
                    unregister = nuke.removeOnCreate

            elif parts[1] == 'removed':
                register = nuke.addOnDestroy
                unregister = nuke.removeOnDestroy

        elif parts[0] == 'knob':
            if parts[1] == 'changed':
                register = nuke.addKnobChanged
                unregister = nuke.removeKnobChanged

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

        elif parts[0] == 'ui':
            if parts[1] == 'update':
                register = nuke.addUpdateUI
                unregister = nuke.removeUpdateUI

        if register is None:
            return super(NukeCallbacks, self).add(name, func, *args, **kwargs)

        # The nodeClass argument causes an error if not set
        if 'nodeClass' in kwargs and kwargs['nodeClass'] is None:
            del kwargs['nodeClass']

        callback = NukeCallbackProxy(name, register, unregister, func, args, kwargs, intercept)

        # Only register if the Nuke window is loaded
        if self.gui is not None and not self.gui._isHiddenNk:
            callback.register()

        self._callbacks.append(callback)
        return callback
