# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np
from vispy import scene
from vispy import visuals

from colour_analysis.nodes import (
    RGB_colourspace_gamut_node,
    RGB_scatter_node,
    spectral_locus_node)

reference_colourspace = 'CIE UCS'

canvas = scene.SceneCanvas(keys='interactive', show=True)

view = canvas.central_widget.add_view()
camera = scene.cameras.TurntableCamera(fov=45,
                                       parent=view.scene,
                                       up='+z')
view.camera = camera

rec_709 = RGB_colourspace_gamut_node(
    reference_colourspace=reference_colourspace,
    parent=view.scene)

red_color4 = RGB_colourspace_gamut_node(
    'REDcolor4',
    reference_colourspace=reference_colourspace,
    wireframe=False,
    parent=view.scene)

transform = visuals.transforms.AffineTransform()
transform.translate((1, 0, 0))
red_color4.transform = transform

aces_cg = RGB_colourspace_gamut_node(
    'ACEScg',
    reference_colourspace=reference_colourspace,
    uniform_colour=(1.0, 1.0, 1.0),
    uniform_opacity=1.0,
    wireframe_colour='k',
    wireframe_opacity=0.5,
    parent=view.scene)

spectral_locus = spectral_locus_node(
    reference_colourspace=reference_colourspace,
    parent=view.scene)

transform = visuals.transforms.AffineTransform()
transform.translate((2, 0, 0))
aces_cg.transform = transform

RGB_scatter = RGB_scatter_node(
    np.random.random((50000, 3)),
    reference_colourspace=reference_colourspace,
    parent=view)

axis = scene.visuals.XYZAxis(parent=view.scene)

text = scene.visuals.Text('Origin',
                          pos=(0.0, 0.0, 0.0),
                          font_size=32,
                          color='w', parent=view.scene)

canvas.app.run()
