# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Chromaticity Diagram Visuals
============================

Defines the *Chromaticity Diagram Visuals*:

-   :func:`CIE_1931_chromaticity_diagram`
-   :func:`CIE_1960_UCS_chromaticity_diagram`
-   :func:`CIE_1976_UCS_chromaticity_diagram`
"""
import colour.algebra
import numpy as np
from pygfx import (
    Geometry,
    Line,
    LineSegmentMaterial,
    Mesh,
    MeshAbstractMaterial,
    MeshBasicMaterial,
)
from scipy.spatial import ConvexHull, Delaunay

from colour import XYZ_to_sRGB
from colour.algebra import normalise_maximum
from colour.hints import ArrayLike
from colour.plotting import (
    CONSTANTS_COLOUR_STYLE,
    XYZ_to_plotting_colourspace,
    filter_cmfs,
)
from colour.utilities import first_item, full, tstack

from colour_analysis.utilities import (
    METHODS_CHROMATICITY_DIAGRAM,
    append_alpha_channel,
    as_contiguous_array,
)
from colour_analysis.constants import DEFAULT_FLOAT_DTYPE, DEFAULT_INT_DTYPE
from colour_analysis.visuals import Primitive

__author__ = "Colour Developers"
__copyright__ = "Copyright 2013 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "VisualChromaticityDiagram",
    "CIE_1931_chromaticity_diagram",
    "CIE_1960_UCS_chromaticity_diagram",
    "CIE_1976_UCS_chromaticity_diagram",
]


class VisualChromaticityDiagram(Mesh):
    """
    Create a chromaticity diagram visual.
    """

    def __init__(
        self,
        samples=32,
        cmfs="CIE 1931 2 Degree Standard Observer",
        method="CIE 1931",
        material: MeshAbstractMaterial = MeshBasicMaterial,
        colors: ArrayLike | None = None,
        opacity: float = 0.5,
        wireframe: bool = False,
    ):
        cmfs = first_item(filter_cmfs(cmfs).values())

        illuminant = CONSTANTS_COLOUR_STYLE.colour.colourspace.whitepoint

        XYZ_to_ij = METHODS_CHROMATICITY_DIAGRAM[method]["XYZ_to_ij"]
        ij_to_XYZ = METHODS_CHROMATICITY_DIAGRAM[method]["ij_to_XYZ"]

        # CMFS
        ij_l = XYZ_to_ij(cmfs.values, illuminant)

        # Line of Purples
        d = colour.algebra.euclidean_distance(ij_l[0], ij_l[-1])
        ij_p = tstack(
            [
                np.linspace(ij_l[0][0], ij_l[-1][0], int(d * samples)),
                np.linspace(ij_l[0][1], ij_l[-1][1], int(d * samples)),
            ]
        )

        # Grid
        triangulation = Delaunay(ij_l, qhull_options="QJ")
        samples = np.linspace(0, 1, samples)
        ii_g, jj_g = np.meshgrid(samples, samples)
        ij_g = tstack([ii_g, jj_g])
        ij_g = ij_g[triangulation.find_simplex(ij_g) > 0]

        ij = np.vstack([ij_l, illuminant, ij_p, ij_g])
        triangulation = Delaunay(ij, qhull_options="QJ")
        positions = np.hstack(
            [ij, np.full((ij.shape[0], 1), 0, DEFAULT_FLOAT_DTYPE)]
        )

        if colors is None:
            colors = normalise_maximum(
                XYZ_to_plotting_colourspace(
                    ij_to_XYZ(positions[..., :2], illuminant), illuminant
                ),
                axis=-1,
            )
        else:
            colors = np.tile(colors, (positions.shape[0], 1))

        geometry = Geometry(
            positions=as_contiguous_array(positions),
            indices=as_contiguous_array(
                triangulation.simplices, DEFAULT_INT_DTYPE
            ),
            colors=as_contiguous_array(append_alpha_channel(colors, opacity)),
        )

        super().__init__(
            geometry,
            material(vertex_colors=True, wireframe=wireframe)
            if wireframe
            else material(vertex_colors=True),
        )


def VisualChromaticityDiagram_CIE1931(
    samples=32, cmfs="CIE 1931 2 Degree Standard Observer", **kwargs
):
    """
    Create the *CIE 1931* chromaticity diagram visual.
    """

    return VisualChromaticityDiagram(samples, cmfs, "CIE 1931", **kwargs)


def VisualChromaticityDiagram_CIE1960UCS(
    samples=32, cmfs="CIE 1931 2 Degree Standard Observer", **kwargs
):
    """
    Create the*CIE 1976 UCS* chromaticity diagram visual.
    """

    return VisualChromaticityDiagram(samples, cmfs, "CIE 1960 UCS", **kwargs)


def VisualChromaticityDiagram_CIE1976UCS(
    samples=32, cmfs="CIE 1931 2 Degree Standard Observer", **kwargs
):
    """
    Create the*CIE 1960 UCS* chromaticity diagram visual.
    """

    return VisualChromaticityDiagram(samples, cmfs, "CIE 1976 UCS", **kwargs)


if __name__ == "__main__":
    from pygfx import (
        Background,
        BackgroundMaterial,
        Display,
        Scene,
    )

    scene = Scene()

    scene.add(
        Background(None, BackgroundMaterial(np.array([0.18, 0.18, 0.18])))
    )

    mesh_1 = VisualChromaticityDiagram_CIE1931()
    scene.add(mesh_1)

    mesh_2 = VisualChromaticityDiagram_CIE1931(wireframe=True)
    mesh_2.local.position = np.array([1, 0, 0])
    scene.add(mesh_2)

    mesh_3 = VisualChromaticityDiagram_CIE1931(colors=[0.36, 0.36, 0.36])
    mesh_3.local.position = np.array([2, 0, 0])
    scene.add(mesh_3)

    mesh_4 = VisualChromaticityDiagram_CIE1960UCS()
    mesh_4.local.position = np.array([3, 0, 0])
    scene.add(mesh_4)

    mesh_5 = VisualChromaticityDiagram_CIE1976UCS()
    mesh_5.local.position = np.array([4, 0, 0])
    scene.add(mesh_5)

    display = Display()
    display.show(scene, up=np.array([0, 0, 1]))
