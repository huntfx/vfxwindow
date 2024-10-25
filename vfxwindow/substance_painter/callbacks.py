from __future__ import absolute_import

from functools import partial

import substance_painter as sp

from ..abstract.callbacks import AbstractCallbacks, CallbackProxy


class SubstancePainterCallbackProxy(CallbackProxy):

    def forceUnregister(self):
        """Unregister the callback without any extra checks."""
        self._unregister(self.func)


class SubstancePainterCallbacks(AbstractCallbacks):
    """Substance Painter callbacks.

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

    CallbackProxy = SubstancePainterCallbackProxy

    def _setupAliases(self):
        """Setup Substance Painter callback aliases."""
        events = {
            'file.new': sp.event.ProjectCreated,
            'file.load': sp.event.ProjectOpened,
            'file.save.before': sp.event.ProjectAboutToSave,
            'file.save.after': sp.event.ProjectSaved,
            'file.close.before': sp.event.ProjectAboutToClose,
            'export.textures.before': sp.event.ExportTexturesAboutToStart,
            'export.textures.after': sp.event.ExportTexturesEnded,
            'shelf.crawling.before': sp.event.ShelfCrawlingStarted,
            'shelf.crawling.after': sp.event.ShelfCrawlingEnded
        }
        for alias, event in events.items():
            register = partial(sp.event.DISPATCHER.connect_strong, event)
            unregister = partial(sp.event.DISPATCHER.disconnect, event)

            if alias.endswith('.after') or alias == 'file.close.before':
                self.aliases[alias.rsplit('.', 1)[0]] = self.aliases[alias] = (register, unregister)
            else:
                self.aliases[alias] = (register, unregister)

    @property
    def registerAvailable(self):
        """Only register if the GUI is loaded."""
        return self.gui is not None and not self.gui._isHiddenSP
