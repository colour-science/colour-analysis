# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np
from vispy.color.color_array import ColorArray
from vispy.scene.visuals import Line, Node

from colour import (
    Lab_to_XYZ,
    LCHab_to_Lab,
    POINTER_GAMUT_BOUNDARIES,
    POINTER_GAMUT_DATA,
    POINTER_GAMUT_ILLUMINANT,
    xy_to_XYZ)
from colour.plotting.volume import XYZ_to_reference_colourspace

from colour_analysis.constants import DEFAULT_PLOTTING_ILLUMINANT
from colour_analysis.visuals import Symbol

POINTER_GAMUT_DATA = Lab_to_XYZ(LCHab_to_Lab(POINTER_GAMUT_DATA),
                                POINTER_GAMUT_ILLUMINANT)

POINTER_GAMUT_BOUNDARIES = xy_to_XYZ(POINTER_GAMUT_BOUNDARIES)


def pointer_gamut_visual(reference_colourspace='CIE xyY',
                         size=4.0,
                         edge_size=0.5,
                         uniform_colour=(0.9, 0.9, 0.9),
                         uniform_opacity=0.8,
                         uniform_edge_colour=(0.9, 0.9, 0.9),
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


def pointer_gamut_hull_visual(reference_colourspace='CIE xyY',
                              uniform_colour=(0.9, 0.9, 0.9),
                              uniform_opacity=0.4,
                              width=2.0,
                              parent=None):
    node = Node(parent=parent)

    pointer_gamut_data = np.reshape(POINTER_GAMUT_DATA, (16, -1, 3))
    for i in range(16):
        points = XYZ_to_reference_colourspace(
            np.vstack((pointer_gamut_data[i], pointer_gamut_data[i][0, ...])),
            POINTER_GAMUT_ILLUMINANT,
            reference_colourspace)

        points[np.isnan(points)] = 0

        RGB = ColorArray(uniform_colour, alpha=uniform_opacity).rgba

        line = Line(points,
                    RGB,
                    width=width,
                    parent=node)
    return node


def pointer_gamut_boundaries_visual(reference_colourspace='CIE xyY',
                                    uniform_colour=(0.9, 0.9, 0.9),
                                    uniform_opacity=0.8,
                                    width=2.0,
                                    parent=None):
    XYZ = np.vstack((POINTER_GAMUT_BOUNDARIES,
                     POINTER_GAMUT_BOUNDARIES[0, ...]))

    illuminant = DEFAULT_PLOTTING_ILLUMINANT

    points = XYZ_to_reference_colourspace(XYZ,
                                          illuminant,
                                          reference_colourspace)
    points[np.isnan(points)] = 0

    RGB = ColorArray(uniform_colour, alpha=uniform_opacity).rgba

    line = Line(points,
                RGB,
                width=width,
                method='agg',
                parent=parent)

    return line
