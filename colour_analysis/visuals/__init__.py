# -*- coding: utf-8 -*-



from .primitive import Primitive, PrimitiveVisual
from .symbol import Symbol
from .axis import axis_visual
from .box import Box, BoxVisual
from .diagrams import (
    VisualChromaticityDiagram_CIE1931,
    VisualChromaticityDiagram_CIE1960UCS,
    VisualChromaticityDiagram_CIE1976UCS,
)
from .image import image_visual
from .plane import Plane, PlaneVisual
from .pointer_gamut import (
    pointer_gamut_boundaries_visual,
    pointer_gamut_hull_visual,
    pointer_gamut_visual,
)
from .colourspace import (
    VisualRGBColourspace3d,
    VisualRGBColourspace2d,
)
from .scatter import VisualRGBScatter3d
from .spectral_locus import (
    spectral_locus_visual,
    chromaticity_diagram_construction_visual,
)

__all__ = []
__all__ += ["Primitive", "PrimitiveVisual"]
__all__ += ["Symbol"]
__all__ += ["Axis", "AxisVisual", "axis_visual"]
__all__ += ["Box", "BoxVisual"]
__all__ += [
    "VisualChromaticityDiagram_CIE1931",
    "VisualChromaticityDiagram_CIE1960UCS",
    "VisualChromaticityDiagram_CIE1976UCS",
]
__all__ += ["image_visual"]
__all__ += ["Plane", "PlaneVisual"]
__all__ += [
    "pointer_gamut_boundaries_visual",
    "pointer_gamut_hull_visual",
    "pointer_gamut_visual",
]
__all__ += [
    "VisualRGBColourspace3d",
    "VisualRGBColourspace2d",
]
__all__ += ["RGB_scatter_visual"]
__all__ += [
    "spectral_locus_visual",
    "chromaticity_diagram_construction_visual",
]
