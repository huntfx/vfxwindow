from __future__ import absolute_import

from functools import partial

import bpy

from ..abstract.callbacks import Alias, AbstractCallbacks, CallbackProxy
from .application import Application


class BlenderCallbackProxy(CallbackProxy):

    def forceUnregister(self):
        """Unregister the callback without any extra checks."""
        self.alias.unregister(self.func)


class _MultiHandler(object):
    """Wrap multiple handlers into one while keeping the same behaviour."""

    def __init__(self, *handlers):
        self.handlers = [getattr(bpy.app.handlers, n) for n in handlers]

    def __contains__(self, func):
        return any(func in handler for handler in self.handlers)

    def append(self, func):
        for handler in self.handlers:
            handler.append(func)

    def remove(self, func):
        for handler in self.handlers:
            handler.remove(func)


class BlenderCallbacks(AbstractCallbacks):
    """Blender callbacks.

    By default handlers are freed when loading new files, but the
    `bpy.app.handlers.persistent` decorator can be used to keep them
    loaded.

    Note that older versions of Blender may be missing some of these.
    Any callback that does not exist will not have its alias registered,
    so a KeyError will occur when adding the callback.

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
            Mapped to 'render.after'.

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

        render.frame.before:
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
            Signature: (None, None) -> None

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
            Mapped to 'frame.changed.after'.

        frame.changed.before:
            Called after frame change for playback and rendering,
            before any data is evaluated for the new frame.
            Signature: (scene: bpy.types.Scene, None) -> None

        frame.changed.after:
            Called after frame change for playback and rendering,
            after the data has been evaluated for the new frame.
            Signature: (scene: bpy.types.Scene, depsgraph: bpy.types.Depsgraph) -> None

        playback:
            Called when starting or ending animation playback.
            Signature: (scene: bpy.types.Scene, depsgraph: bpy.types.Depsgraph) -> None

        playback.start:
            Called when starting animation playback.
            Signature: (scene: bpy.types.Scene, depsgraph: bpy.types.Depsgraph) -> None

        playback.stop:
            Called when ending animation playback.
            Signature: (scene: bpy.types.Scene, depsgraph: bpy.types.Depsgraph) -> None

        scene.update:
            Mapped to `scene.update.after`.

        scene.update.before:
            Before the scene data updates.
            Signature: (scene: bpy.types.Scene, depsgraph: bpy.types.Depsgraph) -> None
            *The `depsgraph` argument is not given in versions under Blender 2.8.

        scene.update.after:
            After the scene data updates.
            Signature: (scene: bpy.types.Scene, depsgraph: bpy.types.Depsgraph) -> None
            *The `depsgraph` argument is not given in versions under Blender 2.8.

    Unimplemented:
        game_pre (removed in 2.80):
            On starting the game engine.
        game_post (removed in 2.80):
            On ending the game engine.
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
            'file.load.before': 'load_pre',
            'file.load.after': 'load_post',
            'file.load.fail': 'load_post_fail',
            'file.save.before': 'save_pre',
            'file.save.after': 'save_post',
            'file.save.fail': 'save_post_fail',
            'frame.changed.before': 'frame_change_pre',
            'frame.changed.after': 'frame_change_post',
            'playback': _MultiHandler('animation_playback_pre', 'animation_playback_post'),
            'playback.start': 'animation_playback_pre',
            'playback.stop': 'animation_playback_post',
            'render.before': 'render_init',
            'render.after': _MultiHandler('render_complete', 'render_cancel'),
            'render.complete': 'render_complete',
            'render.cancel': 'render_cancel',
            'render.stats': 'render_stats',
            'render.frame.before': 'render_pre',
            'render.frame.after': 'render_post',
            'render.frame.write': 'render_write',
            'undo.before': 'undo_pre',
            'undo.after': 'undo_post',
            'redo.before': 'redo_pre',
            'redo.after': 'redo_post',
        }
        if Application.version < 2.8:
            handlers['scene.update.before'] = 'scene_update_pre'
            handlers['scene.update.after'] = 'scene_update_post'
        else:
            handlers['scene.update.before'] = 'depsgraph_update_pre'
            handlers['scene.update.after'] = 'depsgraph_update_post'

        for name, callback in handlers.items():
            try:
                if isinstance(callback, _MultiHandler):
                    handler = callback
                else:
                    handler = getattr(bpy.app.handlers, callback)
            except AttributeError:
                continue

            alias = Alias(register=handler.append, unregister=handler.remove, contains=handler.__contains__)
            self.aliases[name] = alias
            if name.endswith('.after'):
                self.aliases[name.rsplit('.', 1)[0]] = alias

