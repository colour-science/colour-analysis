# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Chromaticity Diagram Visuals
============================

Defines the *Chromaticity Diagram Visuals*:

-   :def:`CIE_1931_chromaticity_diagram`
-   :def:`CIE_1960_UCS_chromaticity_diagram`
-   :def:`CIE_1976_UCS_chromaticity_diagram`
"""

from __future__ import division, unicode_literals

import numpy as np
from scipy.spatial import Delaunay

from colour import (
    XYZ_to_sRGB,
    normalise_maximum,
    tstack)
from colour.plotting import get_cmfs

from colour_analysis.utilities import CHROMATICITY_DIAGRAM_TRANSFORMATIONS
from colour_analysis.constants import DEFAULT_PLOTTING_ILLUMINANT
from colour_analysis.visuals import Primitive


__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013-2016 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['chromaticity_diagram_visual',
           'CIE_1931_chromaticity_diagram',
           'CIE_1960_UCS_chromaticity_diagram',
           'CIE_1976_UCS_chromaticity_diagram']


def chromaticity_diagram_visual(
        samples=256,
        cmfs='CIE 1931 2 Degree Standard Observer',
        transformation='CIE 1931',
        parent=None):
    """
    Creates a chromaticity diagram visual based on
    :class:`colour_analysis.visuals.Primitive` class.

    Parameters
    ----------
    samples : int, optional
        Inner samples count used to construct the chromaticity diagram
        triangulation.
    cmfs : unicode, optional
        Standard observer colour matching functions used for the chromaticity
        diagram boundaries.
    transformation : unicode, optional
        {'CIE 1931', 'CIE 1960 UCS', 'CIE 1976 UCS'}

        Chromaticity diagram transformation.
    parent : Node, optional
        Parent of the chromaticity diagram in the `SceneGraph`.

    Returns
    -------
    Primitive
        Chromaticity diagram visual.
    """

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

    ij_p = np.hstack((ij, np.full((ij.shape[0], 1, np.float_), 0)))
    triangulation = Delaunay(ij, qhull_options='QJ')
    RGB = normalise_maximum(XYZ_to_sRGB(ij_to_XYZ(ij, illuminant), illuminant),
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
    """
    Creates the *CIE 1931* chromaticity diagram visual based on
    :class:`colour_analysis.visuals.Primitive` class.

    Parameters
    ----------
    samples : int, optional
        Inner samples count used to construct the *CIE 1931* chromaticity
        diagram triangulation.
    cmfs : unicode, optional
        Standard observer colour matching functions used for the chromaticity
        diagram boundaries.
    parent : Node, optional
        Parent of the *CIE 1931* chromaticity diagram in the `SceneGraph`.

    Returns
    -------
    Primitive
        *CIE 1931* chromaticity diagram visual.
    """

    return chromaticity_diagram_visual(samples, cmfs, 'CIE 1931', parent)


def CIE_1960_UCS_chromaticity_diagram(
        samples=256,
        cmfs='CIE 1931 2 Degree Standard Observer',
        parent=None):
    """
    Creates the *CIE 1960 UCS* chromaticity diagram visual based on
    :class:`colour_analysis.visuals.Primitive` class.

    Parameters
    ----------
    samples : int, optional
        Inner samples count used to construct the *CIE 1960 UCS* chromaticity
        diagram triangulation.
    cmfs : unicode, optional
        Standard observer colour matching functions used for the chromaticity
        diagram boundaries.
    parent : Node, optional
        Parent of the *CIE 1960 UCS* chromaticity diagram in the `SceneGraph`.

    Returns
    -------
    Primitive
        *CIE 1960 UCS* chromaticity diagram visual.
    """

    return chromaticity_diagram_visual(samples, cmfs, 'CIE 1960 UCS', parent)


def CIE_1976_UCS_chromaticity_diagram(
        samples=256,
        cmfs='CIE 1931 2 Degree Standard Observer',
        parent=None):
    """
    Creates the *CIE 1976 UCS* chromaticity diagram visual based on
    :class:`colour_analysis.visuals.Primitive` class.

    Parameters
    ----------
    samples : int, optional
        Inner samples count used to construct the *CIE 1976 UCS* chromaticity
        diagram triangulation.
    cmfs : unicode, optional
        Standard observer colour matching functions used for the chromaticity
        diagram boundaries.
    parent : Node, optional
        Parent of the *CIE 1976 UCS* chromaticity diagram in the `SceneGraph`.

    Returns
    -------
    Primitive
        *CIE 1976 UCS* chromaticity diagram visual.
    """

    return chromaticity_diagram_visual(samples, cmfs, 'CIE 1976 UCS', parent)
