# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np

from colour import (
    XYZ_to_sRGB,
    normalise,
    tstack)

from colour_analysis.utilities import (
    CHROMATICITY_DIAGRAM_TRANSFORMATIONS,
    get_cmfs)
from colour_analysis.constants import DEFAULT_PLOTTING_ILLUMINANT
from colour_analysis.visuals import Primitive


def chromaticity_diagram_visual(
        samples=256,
        cmfs='CIE 1931 2 Degree Standard Observer',
        transformation='CIE 1931',
        parent=None):
    from scipy.spatial import Delaunay

    cmfs = get_cmfs(cmfs)

    illuminant = DEFAULT_PLOTTING_ILLUMINANT

    XYZ_to_ij = (
        CHROMATICITY_DIAGRAM_TRANSFORMATIONS[transformation]['XYZ_to_ij'])
    ij_to_XYZ = (
        CHROMATICITY_DIAGRAM_TRANSFORMATIONS[transformation]['ij_to_XYZ'])

    ij_c = XYZ_to_ij(cmfs.values, illuminant)

    triangulation = Delaunay(ij_c, qhull_options='QJ')
    samples = np.linspace(0, 1, samples)
    ii, jj = np.meshgrid(samples, samples)
    ij = tstack((ii, jj))
    ij = np.vstack((ij_c, ij[triangulation.find_simplex(ij) > 0]))

    ij_p = np.hstack((ij, np.full((ij.shape[0], 1), 0)))
    triangulation = Delaunay(ij, qhull_options='QJ')
    RGB = normalise(XYZ_to_sRGB(ij_to_XYZ(ij, illuminant), illuminant),
                    axis=-1)

    diagram = Primitive(vertices=ij_p,
                        faces=triangulation.simplices,
                        vertex_colours=RGB,
                        parent=parent)

    return diagram


def CIE_1931_chromaticity_diagram(
        samples=256,
        cmfs='CIE 1931 2 Degree Standard Observer',
        parent=None):
    return chromaticity_diagram_visual(samples, cmfs, 'CIE 1931', parent)


def CIE_1960_UCS_chromaticity_diagram(
        samples=256,
        cmfs='CIE 1931 2 Degree Standard Observer',
        parent=None):
    return chromaticity_diagram_visual(samples, cmfs, 'CIE 1960 UCS', parent)


def CIE_1976_UCS_chromaticity_diagram(
        samples=256,
        cmfs='CIE 1931 2 Degree Standard Observer',
        parent=None):
    return chromaticity_diagram_visual(samples, cmfs, 'CIE 1976 UCS', parent)

