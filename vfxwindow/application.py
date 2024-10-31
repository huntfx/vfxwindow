"""Access all the application classes"""

__all__ = [
    'Blender',
    'CryEngine',
    'Fusion',
    'Houdini',
    'Katana',
    'Max',
    'Maya',
    'Natron',
    'Nuke',
    'SubstanceDesigner',
    'SubstancePainter',
    'Unreal'
]

from .blender.application import Application as Blender
from .cryengine.application import Application as CryEngine
from .fusion.application import Application as Fusion
from .houdini.application import Application as Houdini
from .katana.application import Application as Katana
from .max.application import Application as Max
from .maya.application import Application as Maya
from .natron.application import Application as Natron
from .nuke.application import Application as Nuke
from .renderdoc.application import Application as RenderDoc
from .substance_designer.application import Application as SubstanceDesigner
from .substance_painter.application import Application as SubstancePainter
from .unreal.application import Application as Unreal
