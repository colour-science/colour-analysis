#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

from collections import OrderedDict, namedtuple

import numpy as np
from vispy.scene.widgets.viewbox import ViewBox
from colour import RGB_COLOURSPACES

from colour_analysis.cameras import OrbitCamera
from colour_analysis.utilities.common import REFERENCE_COLOURSPACES
from colour_analysis.utilities.styles import Styles
from colour_analysis.visuals import (
    RGB_colourspace_visual,
    RGB_scatter_visual,
    axis_visual,
    spectral_locus_visual,
    pointer_gamut_visual)


CameraPreset = namedtuple(
    'CameraPreset',
    ('name',
     'description',
     'reference_colourspace',
     'fov',
     'elevation',
     'azimuth',
     'distance',
     'translate_speed',
     'center',
     'up'))

RGB_colourspaceVisualPreset = namedtuple(
    'RGB_colourspaceVisualPreset',
    ('name',
     'description',
     'segments',
     'uniform_colour',
     'uniform_opacity',
     'wireframe',
     'wireframe_colour',
     'wireframe_opacity'))

AxisPreset = namedtuple(
    'AxisPreset',
    ('name',
     'description',
     'reference_colourspace',
     'scale'))


class GamutView(ViewBox):
    def __init__(self,
                 image=None,
                 input_colourspace='Rec. 709',
                 reference_colourspace='CIE xyY',
                 correlate_colourspace='ACEScg',
                 settings=None,
                 **kwargs):
        ViewBox.__init__(self, **kwargs)

        self.__image = None
        self.image = image
        self.__input_colourspace = None
        self.input_colourspace = input_colourspace
        self.__reference_colourspace = None
        self.reference_colourspace = reference_colourspace
        self.__correlate_colourspace = None
        self.correlate_colourspace = correlate_colourspace

        self.__settings = None
        self.settings = settings

        self.__camera_presets = {}
        self.__visuals_style_presets = OrderedDict()
        self.__axis_presets = {}

        self.__input_colourspace_visual = None
        self.__correlate_colourspace_visual = None
        self.__spectral_locus_visual = None
        self.__RGB_scatter_visual = None
        self.__pointer_gamut_visual = None
        self.__axis_visual = None

        self.__clamp_blacks = False
        self.__clamp_whites = False

        self.__visuals_visibility = None

        self.__create_presets()
        self.__create_visuals()
        self.__attach_visuals()
        self.__create_camera()

    @property
    def image(self):
        """
        Property for **self.__image** private attribute.

        Returns
        -------
        array_like
            self.__image.
        """

        return self.__image

    @image.setter
    def image(self, value):
        """
        Setter for **self.__image** private attribute.

        Parameters
        ----------
        value : array_like
            Attribute value.
        """

        if value is not None:
            assert type(value) in (tuple, list, np.ndarray, np.matrix), (
                ('"{0}" attribute: "{1}" type is not "tuple", "list", '
                 '"ndarray" or "matrix"!').format('image', value))
        self.__image = value

    @property
    def input_colourspace(self):
        """
        Property for **self.__input_colourspace** private attribute.

        Returns
        -------
        unicode
            self.__input_colourspace.
        """

        return self.__input_colourspace

    @input_colourspace.setter
    def input_colourspace(self, value):
        """
        Setter for **self.__input_colourspace** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert type(value) in (str, unicode), (
                ('"{0}" attribute: "{1}" type is not '
                 '"str" or "unicode"!').format('input_colourspace', value))
            assert value in RGB_COLOURSPACES, (
                '"{0}" colourspace not found in factory RGB colourspaces: '
                '"{1}".').format(
                value, ', '.join(sorted(RGB_COLOURSPACES.keys())))
        self.__input_colourspace = value

    @property
    def reference_colourspace(self):
        """
        Property for **self.__reference_colourspace** private attribute.

        Returns
        -------
        unicode
            self.__reference_colourspace.
        """

        return self.__reference_colourspace

    @reference_colourspace.setter
    def reference_colourspace(self, value):
        """
        Setter for **self.__reference_colourspace** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert type(value) in (str, unicode), (
                ('"{0}" attribute: "{1}" type is not '
                 '"str" or "unicode"!').format('reference_colourspace', value))
            assert value in REFERENCE_COLOURSPACES, (
                '"{0}" reference colourspace not found in factory reference '
                'colourspaces: "{1}".').format(
                value, ', '.join(sorted(REFERENCE_COLOURSPACES.keys())))
        self.__reference_colourspace = value

    @property
    def correlate_colourspace(self):
        """
        Property for **self.__correlate_colourspace** private attribute.

        Returns
        -------
        unicode
            self.__correlate_colourspace.
        """

        return self.__correlate_colourspace

    @correlate_colourspace.setter
    def correlate_colourspace(self, value):
        """
        Setter for **self.__correlate_colourspace** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert type(value) in (str, unicode), (
                ('"{0}" attribute: "{1}" type is not '
                 '"str" or "unicode"!').format('correlate_colourspace', value))
            assert value in RGB_COLOURSPACES, (
                '"{0}" colourspace not found in factory RGB colourspaces: '
                '"{1}".').format(value, ', '.join(
                sorted(RGB_COLOURSPACES.keys())))
        self.__correlate_colourspace = value


    @property
    def settings(self):
        """
        Property for **self.__settings** private attribute.

        Returns
        -------
        dict
            self.__settings.
        """

        return self.__settings

    @settings.setter
    def settings(self, value):
        """
        Setter for **self.__settings** private attribute.

        Parameters
        ----------
        value : dict
            Attribute value.
        """

        if value is not None:
            assert type(value) is dict, (
                '"{0}" attribute: "{1}" type is not "dict:!'.format(
                    'settings', value))
        self.__settings = value

    def __create_camera_presets(self):
        for camera in self.__settings['cameras']['gamut_view'].values():
            self.__camera_presets[camera['reference_colourspace']] = (
                CameraPreset(
                    name=camera['name'],
                    description=camera['description'],
                    reference_colourspace=camera['reference_colourspace'],
                    fov=camera['fov'],
                    elevation=camera['elevation'],
                    azimuth=camera['azimuth'],
                    distance=camera['distance'],
                    translate_speed=camera['translate_speed'],
                    center=camera['center'],
                    up=camera['up']))

    def __create_visuals_style_presets(self):
        for visual, styles in self.__settings['styles']['gamut_view'].items():
            self.__visuals_style_presets[visual] = []

            for style in styles:
                self.__visuals_style_presets[style['visual']].append(
                    RGB_colourspaceVisualPreset(
                        name=style['name'],
                        description=style['description'],
                        segments=style['segments'],
                        uniform_colour=style['uniform_colour'],
                        uniform_opacity=style['uniform_opacity'],
                        wireframe=style['wireframe'],
                        wireframe_colour=style['wireframe_colour'],
                        wireframe_opacity=style['wireframe_opacity']))

            self.__visuals_style_presets[visual] = Styles(
                self.__visuals_style_presets[visual])

    def __create_axis_presets(self):
        for axis in self.__settings['axis'].values():
            self.__axis_presets[axis['reference_colourspace']] = (
                AxisPreset(
                    name=axis['name'],
                    description=axis['description'],
                    reference_colourspace=axis['reference_colourspace'],
                    scale=axis['scale']))

    def __create_presets(self):
        self.__create_camera_presets()
        self.__create_visuals_style_presets()
        self.__create_axis_presets()

    def __create_RGB_scatter_image(self):
        image = self.__image

        if self.__clamp_blacks:
            image = np.clip(image, 0, np.inf)

        if self.__clamp_whites:
            image = np.clip(image, -np.inf, 1)

        return image

    def __create_colourspace_visual(self, style, colourspace=None):
        return RGB_colourspace_visual(
            colourspace=colourspace,
            reference_colourspace=self.__reference_colourspace,
            segments=style.segments,
            uniform_colour=style.uniform_colour,
            uniform_opacity=style.uniform_opacity,
            wireframe=style.wireframe,
            wireframe_colour=style.wireframe_colour,
            wireframe_opacity=style.wireframe_opacity)

    def __create_input_colourspace_visual(self, style):
        self.__input_colourspace_visual = (
            self.__create_colourspace_visual(
                style, self.__input_colourspace))

    def __create_correlate_colourspace_visual(self, style):

        self.__correlate_colourspace_visual = (
            self.__create_colourspace_visual(
                style, self.__correlate_colourspace))

    def __create_RGB_scatter_visual(self, RGB):
        self.__RGB_scatter_visual = RGB_scatter_visual(
            RGB, reference_colourspace=self.__reference_colourspace)

    def __create_spectral_locus_visual(self):
        self.__spectral_locus_visual = spectral_locus_visual(
            reference_colourspace=self.__reference_colourspace)

    def __create_axis_visual(self):
        self.__axis_visual = axis_visual(
            scale=self.__axis_presets[self.__reference_colourspace].scale)

    def __create_pointer_gamut_visual(self):
        self.__pointer_gamut_visual = pointer_gamut_visual(
            reference_colourspace=self.__reference_colourspace)

    def __create_visuals(self):
        self.__create_RGB_scatter_visual(self.__create_RGB_scatter_image())
        self.__create_pointer_gamut_visual()
        self.__create_input_colourspace_visual(
            self.__visuals_style_presets[
                'input_colourspace_visual'].current_style())
        self.__create_correlate_colourspace_visual(
            self.__visuals_style_presets[
                'correlate_colourspace_visual'].current_style())
        self.__create_spectral_locus_visual()
        self.__create_axis_visual()

    def __create_camera(self):
        camera_settings = self.__camera_presets[self.__reference_colourspace]

        self.camera = OrbitCamera(
            fov=camera_settings.fov,
            elevation=camera_settings.elevation,
            azimuth=camera_settings.azimuth,
            distance=camera_settings.distance,
            translate_speed=camera_settings.translate_speed,
            center=camera_settings.center,
            up=camera_settings.up)

    def __attach_visuals(self):
        self.__RGB_scatter_visual.add_parent(self.scene)
        self.__pointer_gamut_visual.add_parent(self.scene)
        self.__input_colourspace_visual.add_parent(self.scene)
        self.__correlate_colourspace_visual.add_parent(self.scene)
        self.__spectral_locus_visual.add_parent(self.scene)
        self.__axis_visual.add_parent(self.scene)

    def __detach_visuals(self):
        self.__RGB_scatter_visual.remove_parent(self.scene)
        self.__pointer_gamut_visual.remove_parent(self.scene)
        self.__input_colourspace_visual.remove_parent(self.scene)
        self.__correlate_colourspace_visual.remove_parent(self.scene)
        self.__spectral_locus_visual.remove_parent(self.scene)
        self.__axis_visual.remove_parent(self.scene)

    def __store_visuals_visibility(self):
        visible = OrderedDict()
        visible['RGB_scatter_visual'] = (
            self.__RGB_scatter_visual.visible)
        visible['pointer_gamut_visual'] = (
            self.__pointer_gamut_visual.visible)
        visible['input_colourspace_visual'] = (
            self.__input_colourspace_visual.children[0].visible)
        visible['correlate_colourspace_visual'] = (
            self.__correlate_colourspace_visual.children[0].visible)
        visible['spectral_locus_visual'] = (
            self.__spectral_locus_visual.visible)
        visible['axis_visual'] = (
            self.__axis_visual.visible)

        self.__visuals_visibility = visible

    def __restore_visuals_visibility(self):
        visible = self.__visuals_visibility

        self.__RGB_scatter_visual.visible = visible['RGB_scatter_visual']
        self.__pointer_gamut_visual.visible = visible['pointer_gamut_visual']
        for visual in self.__input_colourspace_visual.children:
            visual.visible = visible['input_colourspace_visual']
        for visual in self.__correlate_colourspace_visual.children:
            visual.visible = visible['correlate_colourspace_visual']
        self.__spectral_locus_visual.visible = (
            visible['spectral_locus_visual'])
        self.__axis_visual.visible = visible['axis_visual']

    def toggle_input_colourspace_visual_visibility_action(self):
        for visual in self.__input_colourspace_visual.children:
            visual.visible = not visual.visible

        return True

    def cycle_input_colourspace_visual_style_action(self):
        self.__detach_visuals()

        self.__create_input_colourspace_visual(
            self.__visuals_style_presets[
                'input_colourspace_visual'].next_style())

        self.__attach_visuals()

        return True

    def toggle_correlate_colourspace_visual_visibility_action(self):
        for visual in self.__correlate_colourspace_visual.children:
            visual.visible = not visual.visible

        return True

    def cycle_correlate_colourspace_visual_style_action(self):
        self.__detach_visuals()

        self.__create_correlate_colourspace_visual(
            self.__visuals_style_presets[
                'correlate_colourspace_visual'].next_style())

        self.__attach_visuals()

        return True

    def toggle_spectral_locus_visual_visibility_action(self):
        self.__spectral_locus_visual.visible = (
            not self.__spectral_locus_visual.visible)

    def cycle_spectral_locus_visual_style_action(self):
        self.__detach_visuals()

        self.__create_spectral_locus_visual()

        self.__attach_visuals()

        return True

    def toggle_RGB_scatter_visual_visibility_action(self):
        self.__RGB_scatter_visual.visible = (
            not self.__RGB_scatter_visual.visible)

        return True

    def cycle_RGB_scatter_visual_style_action(self):
        self.__detach_visuals()

        self.__create_RGB_scatter_visual(self.__create_RGB_scatter_image())

        self.__attach_visuals()

        return True

    def toggle_pointer_gamut_visual_visibility_action(self):
        self.__pointer_gamut_visual.visible = (
            not self.__pointer_gamut_visual.visible)

        return True

    def cycle_pointer_gamut_visual_style_action(self):
        self.__detach_visuals()

        self.__create_pointer_gamut_visual()

        self.__attach_visuals()

        return True

    def cycle_correlate_colourspace_action(self):
        self.__detach_visuals()

        self.__create_correlate_colourspace_visual(
            self.__visuals_style_presets[
                'correlate_colourspace_visual'].current_style())

        self.__attach_visuals()

        return True

    def cycle_reference_colourspace_action(self):
        self.__store_visuals_visibility()
        self.__detach_visuals()
        self.__create_visuals()
        self.__attach_visuals()
        self.__restore_visuals_visibility()

        self.__create_camera()

        return True

    def toggle_axis_visual_visibility_action(self):
        self.__axis_visual.visible = (
            not self.__axis_visual.visible)

        return True

    def toggle_blacks_clamp_action(self):
        self.__clamp_blacks = not self.__clamp_blacks

        self.__store_visuals_visibility()
        self.__detach_visuals()
        self.__create_RGB_scatter_visual(self.__create_RGB_scatter_image())
        self.__attach_visuals()
        self.__restore_visuals_visibility()

        return True

    def toggle_whites_clamp_action(self):
        self.__clamp_whites = not self.__clamp_whites

        self.__store_visuals_visibility()
        self.__detach_visuals()
        self.__create_RGB_scatter_visual(self.__create_RGB_scatter_image())
        self.__attach_visuals()
        self.__restore_visuals_visibility()

        return True
