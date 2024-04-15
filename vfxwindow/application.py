"""Access all the application classes"""

__all__ = [
    'Blender',
    'CryEngine',
    'Fusion',
    'Houdini',
    'Max',
    'Maya',
    'Nuke',
    'SubstanceDesigner',
    'SubstancePainter',
    'Unreal'
]

from .blender.application import Application as Blender
from .cryengine.application import Application as CryEngine
from .fusion.application import Application as Fusion
from .houdini.application import Application as Houdini
from .max.application import Application as Max
from .maya.application import Application as Maya
from .nuke.application import Application as Nuke
from .substance_designer.application import Application as SubstanceDesigner
from .substance_painter.application import Application as SubstancePainter
from .unreal.application import Application as Unreal
