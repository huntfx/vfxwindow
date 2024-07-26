from __future__ import absolute_import

from functools import partial

import bpy

from ..abstract.callbacks import AbstractCallbacks, CallbackProxy


class BlenderCallbackProxy(CallbackProxy):

    def getUnregisterParam(self):
        """Get the parameter to pass to the unregister function."""
        return self.callbackFunc


class BlenderCallbacks(AbstractCallbacks):
    def add(self, name, func, *args, **kwargs):
        """Register a callback handler.

        By default handlers are freed when loading new files, but the
        `bpy.app.handlers.persistent` decorator can be used to keep them
        loaded.

        Callbacks:
            file.load:
                Mapped to 'file.load.after'

            file.load.before:
                Called before loading a blend file.
                Signature: (path: str, None) -> None

            file.load.after:
                Called after loading a blend file.
                Signature: (path: str, None) -> None

            file.load.fail:
                Called after failing to load a blend file.
                Signature: (path: str, None) -> None

            file.save.before:
                Called before saving a blend file.
                Signature: (path: str, None) -> None

            file.save.after:
                Called after saving a blend file.
                Signature: (path: str, None) -> None

            file.save.fail:
                Called after failing to save a blend file.
                Signature: (path: str, None) -> None

            render:
                Mapped to 'render.after'.

            render.cancel:
                Called after cancelling a render job.
                Signature: (scene: bpy.types.Scene, None) -> None

            render.after:
                Called on completion of render job.
                Signature: (scene: bpy.types.Scene, None) -> None

            render.before:
                Called on initialisation of a render job.
                Signature: (scene: bpy.types.Scene, None) -> None

            render.frame.before
                Called before render.
                Signature: (scene: bpy.types.Scene, None) -> None

            render.frame.after:
                Called after render.
                Signature: (scene: bpy.types.Scene, None) -> None

            render.frame.write:
                Called after writing a render frame.
                Signature: (scene: bpy.types.Scene, context: None) -> None

            render.stats:
                Called when printing render statistics.
                Signataure: (None, None) -> None

            undo.before:
                Called before loading an undo step.
                Signature: (scene: bpy.types.Scene, None) -> None

            undo.after:
                Called after loading an undo step.
                Signature: (scene: bpy.types.Scene, None) -> None

            redo.before:
                Called before loading a redo step.
                Signature: (scene: bpy.types.Scene, None) -> None

            redo.after:
                Called after loading a redo step.
                Signature: (scene: bpy.types.Scene, None) -> None

            frame.changed:
                Mapped to 'frame.change.after'

            frame.changed.before
                Called after frame change for playback and rendering,
                before any data is evaluated for the new frame.
                Signature: (scene: bpy.types.Scene, None) -> None

            frame.changed.after:
                Called after frame change for playback and rendering,
                after the data has been evaluated for the new frame.
                Signature: (scene: bpy.types.Scene, depsgraph: bpy.types.Depsgraph) -> None

            frame.playback.before:
                Called when starting animation playback.
                Signature: (scene: bpy.types.Scene, depsgraph: bpy.types.Depsgraph) -> None

            frame.playback.after:
                Called when ending animation playback.
                Signature: (scene: bpy.types.Scene, depsgraph: bpy.types.Depsgraph) -> None

        Unimplemented:
            game_pre (removed in 2.80):
                On starting the game engine.
            game_post (removed in 2.80):
                On ending the game engine.
            scene_update_pre (removed in 2.80):
                Called before every scene data update.
                Deprecated by 'depsgraph_update_pre'
            scene_update_post (removed in 2.80):
                Called after every scene data update.
                Deprecated by 'depsgraph_update_post'
            depsgraph.update.before (depsgraph_update_pre):
                Called before Depsgraph update.
            depsgraph.update.after (depsgraph_update_post):
                Called after Depsgraph update.
            load_factory_preferences_post:
                Called after loading factory preferences.
            load_factory_startup_post:
                Called after loading factory startup.
            annotation.before (annotation_pre):
                Called before drawing an annotation.
            annotation.after (annotation_post):
                Called after drawing an annotation.
            composite.cancel (composite_cancel):
                Called when cancelling a compositing background job.
            composite.before (composite_pre):
                Called before a compositing background job.
            composite.after (composite_post):
                Called after a compositing background job.
            bake.cancel (object_bake_cancel):
                Called after cancelling a bake job.
            bake.complete (object_bake_complete):
                Called after completing a bake job.
            bake.before (object_bake_pre):
                Called before starting a bake job.
            translation_update_post:
                Called on translation settings update.
            version_update:
                Called when the versioning code ends.
            xr_session_start_pre:
                Called before starting an xr session.
        """
        parts = name.split('.') + [None, None, None]
        handler = None

        if parts[0] == 'file':
            if parts[1] == 'load':
                if parts[2] == 'before':
                    handler = bpy.app.handlers.load_pre
                elif parts[2] in ('after', None):
                    handler = bpy.app.handlers.load_post
                elif parts[2] == 'fail':
                    handler = bpy.app.handlers.load_post_fail

            elif parts[1] == 'save':
                if parts[2] == 'before':
                    handler = bpy.app.handlers.save_pre
                elif parts[2] in ('after', None):
                    handler = bpy.app.handlers.save_post
                elif parts[2] == 'fail':
                    handler = bpy.app.handlers.save_post_fail

        elif parts[0] == 'frame':
            if parts[1] == 'changed':
                if parts[2] == 'before':
                    handler = bpy.app.handlers.frame_change_pre
                elif parts[2] in ('after', None):
                    handler = bpy.app.handlers.frame_change_post
            elif parts[1] == 'playback':
                if parts[2] == 'before':
                    handler = bpy.app.handlers.animation_playback_pre
                elif parts[2] in ('after', None):
                    handler = bpy.app.handlers.animation_playback_post

        elif parts[0] == 'render':
            if parts[1] == 'cancel':
                handler = bpy.app.handlers.render_cancel
            elif parts[1] == 'before':
                handler = bpy.app.handlers.render_init
            elif parts[1] in ('after', None):
                handler = bpy.app.handlers.render_complete
            elif parts[1] == 'stats':
                handler = bpy.app.handlers.render_stats

            elif parts[1] == 'frame':
                if parts[2] == 'before':
                    handler = bpy.app.handlers.render_pre
                elif parts[2] in ('after', None):
                    handler = bpy.app.handlers.render_post
                elif parts[2] == 'write':
                    handler = bpy.app.handlers.render_write

        elif parts[0] == 'undo':
            if parts[1] == 'before':
                handler = bpy.app.handlers.undo_pre
            elif parts[1] in ('after', None):
                handler = bpy.app.handlers.undo_post

        elif parts[0] == 'redo':
            if parts[1] == 'before':
                handler = bpy.app.handlers.redo_pre
            elif parts[1] in ('after', None):
                handler = bpy.app.handlers.redo_post

        if handler is None:
            return None

        callback = BlenderCallbackProxy(name, handler.append, handler.remove, func, args, kwargs).register()
        self._callbacks.append(callback)
        return callback
