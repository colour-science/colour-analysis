# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RGB Colourspace Visuals
=======================

Defines the *RGB Colourspace Visuals*:

-   :func:`VisualRGBColourspace3d`
-   :func:`VisualRGBColourspace2d`
"""

import numpy as np

from pygfx import (
    Geometry,
    Line,
    LineSegmentMaterial,
    Mesh,
    MeshAbstractMaterial,
    MeshBasicMaterial,
)

from colour import RGB_to_XYZ, XYZ_to_RGB, xy_to_XYZ
from colour.constants import EPSILON
from colour.geometry import primitive_cube
from colour.hints import ArrayLike, Literal
from colour.plotting import CONSTANTS_COLOUR_STYLE, filter_RGB_colourspaces
from colour.plotting.volume import colourspace_model_axis_reorder
from colour.utilities import first_item

from colour_analysis.utilities import (
    METHODS_CHROMATICITY_DIAGRAM,
    XYZ_to_colourspace_model,
    append_alpha_channel,
    as_contiguous_array,
    conform_primitive_dtype,
)

__author__ = "Colour Developers"
__copyright__ = "Copyright 2013 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "VisualRGBColourspace3d",
    "VisualRGBColourspace2d",
]


class VisualRGBColourspace3d(Mesh):
    def __init__(
        self,
        colourspace: str = "ITU-R BT.709",
        colourspace_model: str = "CIE xyY",
        segments: int = 16,
        material: MeshAbstractMaterial = MeshBasicMaterial,
        colors: ArrayLike | None = None,
        opacity: float = 0.5,
        wireframe: bool = False,
    ):
        """
        Create a *RGB* colourspace 3d volume visual.
        """

        colourspace = first_item(filter_RGB_colourspaces(colourspace).values())

        vertices, faces, outline = conform_primitive_dtype(
            primitive_cube(
                width_segments=segments,
                height_segments=segments,
                depth_segments=segments,
            )
        )

        positions = vertices["position"] + 0.5

        if colors is None:
            colors = positions
        else:
            colors = np.tile(colors, (positions.shape[0], 1))

        positions[positions == 0] = EPSILON
        XYZ = RGB_to_XYZ(positions, colourspace)
        positions = colourspace_model_axis_reorder(
            XYZ_to_colourspace_model(
                XYZ, colourspace.whitepoint, colourspace_model
            ),
            colourspace_model,
        )

        geometry = Geometry(
            positions=as_contiguous_array(positions),
            normals=vertices["normal"],
            indices=faces,
            colors=as_contiguous_array(append_alpha_channel(colors, opacity)),
        )

        super().__init__(
            geometry,
            material(vertex_colors=True, wireframe=wireframe)
            if wireframe
            else material(vertex_colors=True),
        )


class VisualRGBColourspace2d(Line):
    def __init__(
        self,
        colourspace: str = "ITU-R BT.709",
        chromaticity_diagram: str = "CIE 1931",
        colors: ArrayLike | None = None,
        opacity: float = 0.5,
        thickness: float = 3.0,
    ):
        """
        Create a *RGB* colourspace 2d gamut visual.
        """

        colourspace = first_item(filter_RGB_colourspaces(colourspace).values())

        plotting_colourspace = CONSTANTS_COLOUR_STYLE.colour.colourspace

        XYZ_to_ij = METHODS_CHROMATICITY_DIAGRAM[chromaticity_diagram][
            "XYZ_to_ij"
        ]

        ij = XYZ_to_ij(
            xy_to_XYZ(colourspace.primaries), plotting_colourspace.whitepoint
        )
        ij[np.isnan(ij)] = 0

        positions = append_alpha_channel(
            np.array([ij[0], ij[1], ij[1], ij[2], ij[2], ij[0]]), 0
        )

        if colors is None:
            RGB = XYZ_to_RGB(
                xy_to_XYZ(colourspace.primaries), plotting_colourspace
            )
            colors = np.array([RGB[0], RGB[1], RGB[1], RGB[2], RGB[2], RGB[0]])
        else:
            colors = np.tile(colors, (positions.shape[0], 1))

        geometry = Geometry(
            positions=as_contiguous_array(positions),
            colors=as_contiguous_array(append_alpha_channel(colors, opacity)),
        )

        super().__init__(
            geometry,
            LineSegmentMaterial(thickness=thickness, vertex_colors=True),
        )


if __name__ == "__main__":
    from pygfx import (
        AmbientLight,
        Background,
        BackgroundMaterial,
        DirectionalLight,
        Display,
        MeshStandardMaterial,
        MeshNormalMaterial,
        Scene,
    )

    scene = Scene()

    scene.add(
        Background(None, BackgroundMaterial(np.array([0.18, 0.18, 0.18])))
    )

    light_1 = AmbientLight()
    scene.add(light_1)

    light_2 = DirectionalLight()
    light_2.local.position = np.array([1, 1, 0])
    scene.add(light_2)

    mesh_1 = VisualRGBColourspace3d()
    scene.add(mesh_1)

    mesh_2 = VisualRGBColourspace3d(wireframe=True)
    mesh_2.local.position = np.array([0.5, 0, 0])
    scene.add(mesh_2)

    mesh_3 = VisualRGBColourspace3d(material=MeshNormalMaterial)
    mesh_3.local.position = np.array([1, 0, 0])
    scene.add(mesh_3)

    mesh_4 = VisualRGBColourspace3d(
        colourspace_model="CIE Lab",
        colors=np.array([0.36, 0.36, 0.36]),
        opacity=1,
        material=MeshStandardMaterial,
    )
    mesh_4.local.position = np.array([2.5, 0, 0])
    scene.add(mesh_4)

    mesh_5 = VisualRGBColourspace2d()
    mesh_5.local.position = np.array([3.5, 0, 0])
    scene.add(mesh_5)

    mesh_6 = VisualRGBColourspace2d(
        chromaticity_diagram="CIE 1976 UCS",
        colors=np.array([0.36, 0.36, 0.36]),
        opacity=1,
    )
    mesh_6.local.position = np.array([4.5, 0, 0])
    scene.add(mesh_6)

    display = Display()
    display.show(scene, up=np.array([0, 0, 1]))
