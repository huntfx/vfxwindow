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


# The following applications are not currently implemented:
# Katana (katana):
#     [kK]atana\d+(?:\.\d+){0,2}\.(?:bin|exe|app)
#     [kK]atana\.(?:bin|exe|app)
# Mari (mari):
#     [mM]ari\d+(?:\.\d+){0,2}\.(?:bin|exe|app)
#     [mM]ari\.(?:bin|exe|app)
# Modo (lx):
#     [mM]odo\d+(?:\.\d+){0,2}\.(?:bin|exe|app)
#     [mM]odo\.(?:bin|exe|app)
# Hiero (hiero):
#     [hH]iero\d+(?:\.\d+){0,2}\.(?:bin|exe|app)
#     [hH]iero\.(?:bin|exe|app)
# Motion Builder (pyfbsdk + pyfbsdk_additions):
#     ^.*(?:\\|/)[mM]otion[bB]uilder\d{4}(?:\\|/)[mM]otion[bB]uilder\.(?:bin|exe|app)
#     [mM]otion[bB]uilder\.(?:bin|exe|app)
