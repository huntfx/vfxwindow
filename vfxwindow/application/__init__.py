"""Setup the application data classes."""

__all__ = [
    'Blender',
    'CryEngine',
    'Fusion',
    'Houdini',
    'Maya',
    'Max',
    'Nuke',
    'SubstanceDesigner',
    'SubstancePainter',
    'Unreal',
]

from .blender import BlenderApplication
from .cryengine import CryEngineApplication
from .fusion import FusionApplication
from .houdini import HoudiniApplication
from .maya import MayaApplication
from .max import MaxApplication
from .nuke import NukeApplication
from .substance_designer import SubstanceDesignerApplication
from .substance_painter import SubstancePainterApplication
from .unreal import UnrealApplication


Blender = BlenderApplication()

CryEngine = CryEngineApplication()

Fusion = FusionApplication()

Houdini = HoudiniApplication()

Maya = MayaApplication()

Max = MaxApplication()

Nuke = NukeApplication()

SubstanceDesigner = SubstanceDesignerApplication()

SubstancePainter = SubstancePainterApplication()

Unreal = UnrealApplication()
