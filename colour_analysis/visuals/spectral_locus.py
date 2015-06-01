# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np
from vispy.color.color_array import ColorArray
from vispy.scene.visuals import Line
from colour import XYZ_to_sRGB, normalise

from colour_analysis.constants import DEFAULT_PLOTTING_ILLUMINANT
from colour_analysis.utilities import (
    XYZ_to_reference_colourspace,
    get_cmfs)


def spectral_locus_visual(reference_colourspace='CIE xyY',
                          cmfs='CIE 1931 2 Degree Standard Observer',
                          uniform_colour=None,
                          uniform_opacity=1.0,
                          width=2.0,
                          method='gl',
                          parent=None):
    cmfs = get_cmfs(cmfs)
    XYZ = cmfs.values

    XYZ = np.vstack((XYZ, XYZ[0, ...]))

    illuminant = DEFAULT_PLOTTING_ILLUMINANT

    points = XYZ_to_reference_colourspace(XYZ,
                                          illuminant,
                                          reference_colourspace)
    points[np.isnan(points)] = 0

    if uniform_colour is None:
        RGB = normalise(XYZ_to_sRGB(XYZ, illuminant), axis=-1)
        RGB = np.hstack((RGB, np.full((RGB.shape[0], 1), uniform_opacity)))
    else:
        RGB = ColorArray(uniform_colour, alpha=uniform_opacity).rgba

    line = Line(points,
                np.clip(RGB, 0, 1),
                width=width,
                method=method,
                parent=parent)

    return line
