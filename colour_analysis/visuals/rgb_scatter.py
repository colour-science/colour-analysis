# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np
from vispy.color.color_array import ColorArray
from colour import RGB_to_XYZ

from colour_analysis.utilities import (
    XYZ_to_reference_colourspace,
    get_RGB_colourspace)
from colour_analysis.visuals import Symbol


def RGB_scatter_visual(RGB,
                       colourspace='Rec. 709',
                       reference_colourspace='CIE xyY',
                       symbol='disc',
                       size=4.0,
                       edge_size=0.5,
                       uniform_colour=None,
                       uniform_opacity=1.0,
                       uniform_edge_colour=None,
                       uniform_edge_opacity=1.0,
                       resampling='auto',
                       parent=None):
    colourspace = get_RGB_colourspace(colourspace)

    RGB = np.asarray(RGB)

    if resampling == 'auto':
        resampling = int((0.0078125 * np.average(RGB.shape[0:1])) // 2)

        RGB = RGB[::resampling, ::resampling].reshape((-1, 3))

        XYZ = RGB_to_XYZ(
            RGB,
            colourspace.whitepoint,
            colourspace.whitepoint,
            colourspace.RGB_to_XYZ_matrix)

        points = XYZ_to_reference_colourspace(XYZ,
                                              colourspace.whitepoint,
                                              reference_colourspace)

        points[np.isnan(points)] = 0

        RGB = np.clip(RGB, 0, 1)

        if uniform_colour is None:
            RGB = np.hstack((RGB, np.full((RGB.shape[0], 1), uniform_opacity)))
        else:
            RGB = ColorArray(uniform_colour, alpha=uniform_opacity).rgba

        if uniform_edge_colour is None:
            RGB_e = RGB
        else:
            RGB_e = ColorArray(uniform_edge_colour,
                               alpha=uniform_edge_opacity).rgba

        markers = Symbol(symbol=symbol,
                         points=points,
                         size=size,
                         edge_size=edge_size,
                         face_color=RGB,
                         edge_color=RGB_e,
                         parent=parent)

        return markers
