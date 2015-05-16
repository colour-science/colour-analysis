# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import os

from colour import ILLUMINANTS

RESOURCES_DIRECTORY = os.path.join(os.path.dirname(__file__), 'resources')

SETTINGS_FILE = os.path.join(RESOURCES_DIRECTORY, 'settings.json')

IMAGES_DIRECTORY = os.path.join(RESOURCES_DIRECTORY, 'images')

DEFAULT_IMAGE = os.path.join(IMAGES_DIRECTORY, 'Digital_LAD_2048x1556.exr')

DEFAULT_PLOTTING_ILLUMINANT = ILLUMINANTS.get(
    'CIE 1931 2 Degree Standard Observer').get('D65')

REFERENCE_COLOURSPACES = (
    'CIE XYZ',
    'CIE xyY',
    'CIE Lab',
    'CIE Luv',
    'CIE UCS',
    'CIE UVW',
    'IPT')

REFERENCE_COLOURSPACES_TO_LABELS = {
    'CIE XYZ': ('X', 'Y', 'Z'),
    'CIE xyY': ('x', 'y', 'Y'),
    'CIE Lab': ('a', 'b', '$L^*$'),
    'CIE Luv': ('$u^\prime$', '$v^\prime$', '$L^*$'),
    'CIE UCS': ('U', 'V', 'W'),
    'CIE UVW': ('U', 'V', 'W'),
    'IPT': ('P', 'T', 'I')}
"""
Reference colourspaces to labels mapping.

REFERENCE_COLOURSPACES_TO_LABELS : dict
    **{'CIE XYZ', 'CIE xyY', 'CIE Lab', 'CIE Luv', 'CIE UCS', 'CIE UVW',
    'IPT'}**
"""

LINEAR_IMAGE_FORMATS = ('exr', 'hdr')
