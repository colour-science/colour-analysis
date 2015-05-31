#!/usr/bin/env python
# -*- coding: utf-8 -*-

from primitive import Primitive, PrimitiveVisual
from symbol import Symbol
from axis import axis_visual
from box import Box, BoxVisual
from diagrams import (
    CIE_1931_chromaticity_diagram,
    CIE_1960_UCS_chromaticity_diagram,
    CIE_1976_UCS_chromaticity_diagram)
from image import image_visual
from plane import Plane, PlaneVisual
from pointer_gamut import pointer_gamut_visual
from rgb_colourspace import (
    RGB_identity_cube,
    RGB_colourspace_volume_visual,
    RGB_colourspace_triangle_visual)
from rgb_scatter import RGB_scatter_visual
from spectral_locus import spectral_locus_visual

__all__ = []
__all__ += ['Primitive', 'PrimitiveVisual']
__all__ += ['Symbol']
__all__ += ['Axis', 'AxisVisual', 'axis_visual']
__all__ += ['Box', 'BoxVisual']
__all__ += ['CIE_1931_chromaticity_diagram',
            'CIE_1960_UCS_chromaticity_diagram',
            'CIE_1976_UCS_chromaticity_diagram']
__all__ += ['image_visual']
__all__ += ['Plane', 'PlaneVisual']
__all__ += ['pointer_gamut_visual']
__all__ += ['RGB_identity_cube',
            'RGB_colourspace_volume_visual',
            'RGB_colourspace_triangle_visual']
__all__ += ['RGB_scatter_visual']
__all__ += ['spectral_locus_visual']
