from __future__ import absolute_import

from functools import partial

import bpy

from ..abstract.callbacks import AbstractCallbacks, CallbackProxy


class BlenderCallbackProxy(CallbackProxy):

    def forceUnregister(self):
        """Unregister the callback without any extra checks."""
        self._unregister(self.func)

    @property
    def registered(self):
        """Determine if the callback is registered."""
        return self.func in self._register.__self__


class BlenderCallbacks(AbstractCallbacks):
    """Blender callbacks.

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

        file.save:
            Mapped to 'file.save.after'

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
            Mapped to 'render.end'.

        render.before:
            Called on initialisation of a render job.
            Signature: (scene: bpy.types.Scene, None) -> None

        render.complete:
            Called on completion of render job.
            Signature: (scene: bpy.types.Scene, None) -> None

        render.cancel:
            Called after cancelling a render job.
            Signature: (scene: bpy.types.Scene, None) -> None

        render.after:
            Called on completion or cancellation of render job.
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

        playback.start:
            Called when starting animation playback.
            Signature: (scene: bpy.types.Scene, depsgraph: bpy.types.Depsgraph) -> None

        playback.end:
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

    CallbackProxy = BlenderCallbackProxy

    def _setupAliases(self):
        """Setup Blender callback aliases."""
        handlers = {
            'file.load.before': bpy.app.handlers.load_pre,
            'file.load.after': bpy.app.handlers.load_post,
            'file.load.fail': bpy.app.handlers.load_post_fail,
            'file.save.before': bpy.app.handlers.save_pre,
            'file.save.after': bpy.app.handlers.save_post,
            'file.save.fail': bpy.app.handlers.save_post_fail,
            'frame.changed.before': bpy.app.handlers.frame_change_pre,
            'frame.changed.after': bpy.app.handlers.frame_change_post,
            'playback.before': bpy.app.handlers.animation_playback_pre,
            'playback.after': bpy.app.handlers.animation_playback_post,
            'render.before': bpy.app.handlers.render_init,
            'render.complete': bpy.app.handlers.render_complete,
            'render.cancel': bpy.app.handlers.render_cancel,
            'render.stats': bpy.app.handlers.render_stats,
            'render.frame.before': bpy.app.handlers.render_pre,
            'render.frame.after': bpy.app.handlers.render_post,
            'render.frame.write': bpy.app.handlers.render_write,
            'undo.before': bpy.app.handlers.undo_pre,
            'undo.after': bpy.app.handlers.undo_post,
            'redo.before': bpy.app.handlers.redo_pre,
            'redo.after': bpy.app.handlers.redo_post,
        }
        for alias, handler in handlers.items():
            if alias.endswith('.after'):
                self.aliases[alias.rsplit('.', 1)[0]] = self.aliases[alias] = (handler.append, handler.remove)
            else:
                self.aliases[alias] = (handler.append, handler.remove)

        def registerAfterRender(func):
            bpy.app.handlers.render_complete.append(func)
            bpy.app.handlers.render_cancel.append(func)
        def unregisterAfterRender(func):
            bpy.app.handlers.render_complete.append(func)
            bpy.app.handlers.render_cancel.append(func)
        self.aliases['render'] = self.aliases['render.after'] = (registerAfterRender, unregisterAfterRender)
