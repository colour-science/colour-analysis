# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RGB Scatter Visual
==================

Defines the *RGB Scatter Visual*:

-   :func:`RGB_scatter_visual`
"""

import numpy as np

from pygfx import (
    Geometry,
    MeshAbstractMaterial,
    Points,
    PointsMaterial,
)

from colour import RGB_to_XYZ
from colour.constants import EPSILON
from colour.hints import ArrayLike

from colour.plotting import filter_RGB_colourspaces
from colour.plotting.volume import colourspace_model_axis_reorder
from colour.utilities import first_item

from colour_analysis.utilities import (
    XYZ_to_colourspace_model,
    as_float_array,
    as_contiguous_array,
    append_alpha_channel,
)

__author__ = "Colour Developers"
__copyright__ = "Copyright 2013 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = ["VisualRGBScatter3d"]


class VisualRGBScatter3d(Points):
    def __init__(
        self,
        RGB: ArrayLike,
        colourspace: str = "ITU-R BT.709",
        colourspace_model: str = "CIE xyY",
        size: float = 3.0,
        material: MeshAbstractMaterial = PointsMaterial,
        colors: ArrayLike | None = None,
        opacity: float = 0.5,
    ):
        """
        Create a *RGB* 3d scatter visual.
        """

        colourspace = first_item(filter_RGB_colourspaces(colourspace).values())

        RGB = as_float_array(RGB).reshape(-1, 3)

        RGB[RGB == 0] = EPSILON

        XYZ = RGB_to_XYZ(RGB, colourspace)

        positions = colourspace_model_axis_reorder(
            XYZ_to_colourspace_model(
                XYZ, colourspace.whitepoint, colourspace_model
            ),
            colourspace_model,
        )

        if colors is None:
            colors = RGB
        else:
            colors = np.tile(colors, (RGB.shape[0], 1))

        geometry = Geometry(
            positions=as_contiguous_array(positions),
            sizes=as_contiguous_array(np.full(RGB.shape[0], size)),
            colors=as_contiguous_array(append_alpha_channel(colors, opacity)),
        )

        super().__init__(
            geometry,
            material(vertex_colors=True, vertex_sizes=True)
            if material is PointsMaterial
            else material(),
        )


if __name__ == "__main__":
    from pygfx import (
        Background,
        Display,
        BackgroundMaterial,
        Scene,
    )

    scene = Scene()

    scene.add(
        Background(None, BackgroundMaterial(np.array([0.18, 0.18, 0.18])))
    )

    scatter_1 = VisualRGBScatter3d(np.random.random((64, 64, 3)))
    scene.add(scatter_1)

    scatter_2 = VisualRGBScatter3d(
        np.random.random((64, 64, 3)), colors=np.array([0.36, 0.36, 0.36])
    )
    scatter_2.local.position = np.array([0.5, 0, 0])
    scene.add(scatter_2)

    display = Display()
    display.show(scene, up=np.array([0, 0, 1]))
