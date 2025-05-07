from __future__ import absolute_import

from functools import partial

import substance_painter as sp

from ..abstract.callbacks import AbstractCallbacks, CallbackProxy


class SubstancePainterCallbackProxy(CallbackProxy):

    def forceUnregister(self):
        """Unregister the callback without any extra checks."""
        self.alias.unregister(self.func)

    @property
    def registered(self):
        """Determine if the callback is registered.

        The Dispatcher class does not have any public method to use,
        but it stores a private list of every "strong" reference which
        can be used for this case.
        """
        try:
            return self.func in sp.event.DISPATCHER._strong_refs
        except AttributeError:
            return super(SubstancePainterCallbackProxy, self).registered


class SubstancePainterCallbacks(AbstractCallbacks):
    """Substance Painter callbacks.

    Callbacks:
        file.new:
            Called when a new project has been created.
            Signature: (evt: ProjectCreated()) -> None

        file.load:
            Called when an existing project has been opened.
            The project may still be loading at this point.
            Signature: (evt: ProjectOpened()) -> None

        file.close:
            Mapped to 'file.close.before'

        file.close.before:
            Event triggered just before closing the current project.
            Signature: (evt: ProjectAboutToClose()) -> None

        file.save:
            Mapped to 'file.save.after'

        file.save.before:
            Called just before saving the current project.
            Signature: (evt: ProjectAboutToSave(file_path: str)) -> None
                file_path: The destination file.

        file.save.after:
            Called once the current project is saved.
            Signature: (evt: ProjectSaved()) -> None

        texture.export:
            Mapped to 'texture.export.after'

        texture.export.before:
            Called just before a texture export.
            Signature: (evt: ExportTexturesAboutToStart(textures: Dict[Tuple[str, str], List[str]])) -> None
                textures: List of texture files to be written to disk.
                    Grouped by stack (Texture Set name, stack name).

        texture.export.after:
            Signature: (evt: ExportTexturesEnded(message: str, status: sp.export.ExportStatus,
                                                 textures: Dict[Tuple[str, str], List[str]])) -> None
                message: Human readable status message.
                textures: List of texture files written to disk.
                    Grouped by stack (Texture Set name, stack name).

        shelf.crawling.before:
            Called when a shelf starts reading the file system to
            discover new resources.
            Signature: (evt: ShelfCrawlingStarted(shelf_name: str)) -> None

        shelf.crawling.after:
            Called when a shelf has finished discovering new
            resources and loading thumbnails.
            Signature: (evt: ShelfCrawlingEnded(shelf_name: str)) -> None

    Unimplemented
        sp.event.ProjectEditionEntered:
            Called when the project is fully loaded and ready to work with.
            Signature: () -> None

        sp.event.ProjectEditionLeft:
            Called when the current project can non longer be edited.
            Signature: () -> None

        sp.event.BusyStatusChanged:
            Called when Substance 3D Painter busy state changes.
            Signature: (evt: BusyStatusChanged(busy: bool)) -> None

        sp.event.TextureStateEvent:
            Called when a document texture is added, removed or updated.
            Signature: (action: sp.event.TextureStateEventAction, cache_key: int,
                        channel_type: sp.textureset.ChannelType, stack_id: int,
                        tile_indices: Tuple[int, int]) -> None

        sp.event.BakingProcessEnded:
            Called after baking is finished.
            Signature: (evt: Event(status: BakingStatus)) -> None
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
            'texture.export.before': sp.event.ExportTexturesAboutToStart,
            'texture.export.after': sp.event.ExportTexturesEnded,
            'shelf.crawling.before': sp.event.ShelfCrawlingStarted,
            'shelf.crawling.after': sp.event.ShelfCrawlingEnded
        }
        for name, event in events.items():
            register = partial(sp.event.DISPATCHER.connect_strong, event)
            unregister = partial(sp.event.DISPATCHER.disconnect, event)
            alias = (register, unregister)

            self.aliases[name] = alias
            if name.endswith('.after') or name == 'file.close.before':
                self.aliases[name.rsplit('.', 1)[0]] = alias

    @property
    def registerAvailable(self):
        """Only register if the GUI is loaded."""
        return self.gui is not None and not self.gui._isHiddenSP
