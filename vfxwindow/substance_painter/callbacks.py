from __future__ import absolute_import

from functools import partial

import substance_painter as sp

from ..abstract.callbacks import AbstractCallbacks, CallbackProxy


class SubstancePainterCallbackProxy(CallbackProxy):

    def getUnregisterParam(self):
        """Get the parameter to pass to the unregister function."""
        return self.func


class SubstancePainterCallbacks(AbstractCallbacks):
    def add(self, name, func, *args, **kwargs):
        """Register a callback.

        Callbacks:
            file.load:
                Called when an existing project has been opened.
                The project may still be loading at this point.
                Signature: (evt: Event()) -> None

            file.new:
                Called when a new project has been created.
                Signature: (evt: Event()) -> None

            file.close:
                Mapped to 'file.close.before'

            file.close.before:
                Event triggered just before closing the current project.
                Signature: (evt: Event()) -> None

            file.save:
                Mapped to 'file.save.after'

            file.save.before:
                Called just before saving the current project.
                Signature: (evt: Event(file_path: str)) -> None
                    file_path: The destination file.

            file.save.after:
                Called once the current project is saved.
                Signature: (evt: Event()) -> None

            export.textures.before:
                Called just before a textures export.
                Signature: (evt: Event(textures: Dict[Tuple[str, str], List[str]])) -> None
                    textures: List of texture files to be written to disk.
                        Grouped by stack (Texture Set name, stack name).

            export.textures.after:
                Signature: (evt: Event(message: str, status: sp.export.ExportStatus,
                                       textures: Dict[Tuple[str, str], List[str]])) -> None
                    message: Human readable status message.
                    textures: List of texture files written to disk.
                        Grouped by stack (Texture Set name, stack name).

            shelf.crawling.before:
                Called when a shelf starts reading the file system to
                discover new resources.
                Signature: (evt: Event(shelf_name: str)) -> None

            shelf.crawling.after:
                Called when a shelf has finished discovering new
                resources and loading thumbnails.
                Signature: (evt: Event(shelf_name: str)) -> None

        Unimplemented
            sp.event.ProjectEditionEntered:
                Called when the project is fully loaded and ready to work with.
                Signature: () -> None

            sp.event.ProjectEditionLeft:
                Called when the current project can non longer be edited.
                Signature: () -> None

            sp.event.BusyStatusChanged:
                Called when Substance 3D Painter busy state changes.
                Signature: (evt: Event(busy: bool)) -> None

            sp.event.TextureStateEvent:
                Called when a document texture is added, removed or updated.
                Signature: (action: sp.event.TextureStateEventAction, cache_key: int,
                            channel_type: sp.textureset.ChannelType, stack_id: int,
                            tile_indices: Tuple[int, int]) -> None

            sp.event.BakingProcessEnded:
                Called after baking is finished.
                Signature: (evt: Event(status: BakingStatus)):
        """
        parts = name.split('.') + [None, None, None]

        event = None

        if parts[0] == 'file':
            if parts[1] == 'new':
                event = sp.event.ProjectCreated

            elif parts[1] == 'load':
                event = sp.event.ProjectOpened

            elif parts[1] == 'save':
                if parts[2] == 'before':
                    event = sp.event.ProjectAboutToSave
                elif parts[2] in ('after', None):
                    event = sp.event.ProjectSaved

            elif parts[1] == 'close':
                if parts[2] in ('before', None):
                    event = sp.event.ProjectAboutToClose

        elif parts[0] == 'export':
            if parts[1] == 'textures':
                if parts[2] == 'before':
                    event = sp.event.ExportTexturesAboutToStart
                elif parts[2] in ('after', None):
                    event = sp.event.ExportTexturesEnded

        elif parts[0] == 'shelf':
            if parts[1] == 'crawling':
                if parts[2] == 'before':
                    event = sp.event.ShelfCrawlingStarted
                elif parts[2] in ('after', None):
                    event = sp.event.ShelfCrawlingEnded

        if event is None:
            return super(SubstancePainterCallbacks, self).add(name, func, *args, **kwargs)

        register = partial(sp.event.DISPATCHER.connect_strong, event)
        unregister = partial(sp.event.DISPATCHER.disconnect, event)

        callback = SubstancePainterCallbackProxy(name, register, unregister, func, args, kwargs)

        # Only register if the Substance Painter window is loaded
        if self.gui is not None and not self.gui._isHiddenSP:
            callback.register()

        self._callbacks.append(callback)
        return callback

