# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

from vispy.color.color_array import ColorArray
from colour import (
    Lab_to_XYZ,
    LCHab_to_Lab,
    POINTER_GAMUT_DATA,
    POINTER_GAMUT_ILLUMINANT)

from colour_analysis.visuals import Symbol
from colour_analysis.utilities.common import XYZ_to_reference_colourspace

POINTER_GAMUT_DATA = Lab_to_XYZ(LCHab_to_Lab(POINTER_GAMUT_DATA),
                                POINTER_GAMUT_ILLUMINANT)


def pointer_gamut_visual(reference_colourspace='CIE xyY',
                         size=6.0,
                         edge_size=0.5,
                         uniform_colour=(0.8, 0.8, 0.8),
                         uniform_opacity=0.8,
                         uniform_edge_colour=(0.8, 0.8, 0.8),
                         uniform_edge_opacity=0.8,
                         parent=None):
    points = XYZ_to_reference_colourspace(POINTER_GAMUT_DATA,
                                          POINTER_GAMUT_ILLUMINANT,
                                          reference_colourspace)

    RGB = ColorArray(uniform_colour, alpha=uniform_opacity).rgba
    RGB_e = ColorArray(uniform_edge_colour, alpha=uniform_edge_opacity).rgba

    markers = Symbol(symbol='cross',
                     points=points,
                     size=size,
                     edge_size=edge_size,
                     face_color=RGB,
                     edge_color=RGB_e,
                     parent=parent)

    return markers
