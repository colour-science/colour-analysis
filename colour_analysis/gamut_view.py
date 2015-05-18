#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np
from collections import OrderedDict, namedtuple
from vispy.scene.widgets.viewbox import ViewBox

from colour import RGB_COLOURSPACES

from colour_analysis.cameras import OrbitCamera
from colour_analysis.common import REFERENCE_COLOURSPACES
from colour_analysis.styles import Styles
from colour_analysis.visuals import (
    RGB_colourspace_visual,
    RGB_scatter_visual,
    axis_visual,
    spectral_locus_visual)

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

        self.initialise_presets()
        self.initialise_visuals()
        self.initialise_camera()

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

    def __initialise_camera_presets(self):
        cameras = self.__settings['cameras']['gamut_view'].values()
        for camera in cameras:
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

    def __initialise_visuals_style_presets(self):
        visuals_style_settings = self.__settings['styles']['gamut_view']
        for visual, styles in visuals_style_settings.items():
            self.__visuals_style_presets[visual] = []

            for style in styles:
                self.__visuals_style_presets[style['visual']].append(
                    RGB_colourspaceVisualPreset(
                        name=style['name'],
                        description=style['description'],
                        uniform_colour=style['uniform_colour'],
                        uniform_opacity=style['uniform_opacity'],
                        wireframe=style['wireframe'],
                        wireframe_colour=style['wireframe_colour'],
                        wireframe_opacity=style['wireframe_opacity']))

            self.__visuals_style_presets[visual] = Styles(
                self.__visuals_style_presets[visual])

    def __initialise_axis_presets(self):
        axis_presets = self.__settings['axis'].values()
        for axis in axis_presets:
            self.__axis_presets[axis['reference_colourspace']] = (
                AxisPreset(
                    name=axis['name'],
                    description=axis['description'],
                    reference_colourspace=axis['reference_colourspace'],
                    scale=axis['scale']))

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
            uniform_colour=style.uniform_colour,
            uniform_opacity=style.uniform_opacity,
            wireframe=style.wireframe,
            wireframe_colour=style.wireframe_colour,
            wireframe_opacity=style.wireframe_opacity,
            parent=self.scene)

    def __attach_input_colourspace_visual(self, style):
        self.__input_colourspace_visual = (
            self.__create_colourspace_visual(style,
                                             self.__input_colourspace))

    def __detach_input_colourspace_visual(self):
        self.__input_colourspace_visual.remove_parent(self.scene)

    def __attach_correlate_colourspace_visual(self, style):

        self.__correlate_colourspace_visual = (
            self.__create_colourspace_visual(style,
                                             self.__correlate_colourspace))

    def __detach_correlate_colourspace_visual(self):
        self.__correlate_colourspace_visual.remove_parent(
            self.scene)

    def __attach_RGB_scatter_visual(self, RGB):
        self.__RGB_scatter_visual = RGB_scatter_visual(
            RGB,
            reference_colourspace=self.__reference_colourspace,
            parent=self)

    def __detach_RGB_scatter_visual(self):
        self.__RGB_scatter_visual.remove_parent(
            self.scene)

    def __attach_spectral_locus_visual(self):
        self.__spectral_locus_visual = spectral_locus_visual(
            reference_colourspace=self.__reference_colourspace,
            parent=self.scene)

    def __detach_spectral_locus_visual(self):
        self.__spectral_locus_visual.remove_parent(self.scene)

    def __attach_axis_visual(self):
        self.__axis_visual = axis_visual(
            scale=self.__axis_presets[
                self.__reference_colourspace].scale,
            parent=self.scene)

    def __detach_axis_visual(self):
        self.__axis_visual.remove_parent(self.scene)

    def __attach_visuals(self):
        self.__attach_RGB_scatter_visual(self.__create_RGB_scatter_image())

        self.__attach_input_colourspace_visual(
            self.__visuals_style_presets[
                'input_colourspace_visual'].current_style())

        self.__attach_correlate_colourspace_visual(
            self.__visuals_style_presets[
                'correlate_colourspace_visual'].current_style())

        self.__attach_spectral_locus_visual()

        self.__attach_axis_visual()

    def __detach_visuals(self):
        self.__detach_RGB_scatter_visual()

        self.__detach_input_colourspace_visual()

        self.__detach_correlate_colourspace_visual()

        self.__detach_spectral_locus_visual()

        self.__detach_axis_visual()

    def __attach_camera(self):
        camera_settings = self.__camera_presets[self.__reference_colourspace]

        self.camera = OrbitCamera(
            fov=camera_settings.fov,
            elevation=camera_settings.elevation,
            azimuth=camera_settings.azimuth,
            distance=camera_settings.distance,
            translate_speed=camera_settings.translate_speed,
            center=camera_settings.center,
            up=camera_settings.up)

    def __detach_camera(self):
        pass

    def __store_visuals_visibility(self):
        visible = OrderedDict()
        visible['RGB_scatter_visual'] = (
            self.__RGB_scatter_visual.visible)
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
        for visual in self.__input_colourspace_visual.children:
            visual.visible = visible['input_colourspace_visual']
        for visual in self.__correlate_colourspace_visual.children:
            visual.visible = visible['correlate_colourspace_visual']
        self.__spectral_locus_visual.visible = (
            visible['spectral_locus_visual'])
        self.__axis_visual.visible = visible['axis_visual']

    def initialise_presets(self):
        self.__initialise_camera_presets()
        self.__initialise_visuals_style_presets()
        self.__initialise_axis_presets()

        return True

    def initialise_camera(self):
        self.__attach_camera()

        return True

    def initialise_visuals(self):
        self.__attach_visuals()

        return True

    def toggle_input_colourspace_visual_visibility_action(self):
        for visual in self.__input_colourspace_visual.children:
            visual.visible = not visual.visible

        return True

    def cycle_input_colourspace_visual_style_action(self):
        self.__detach_input_colourspace_visual()

        self.__attach_input_colourspace_visual(
            self.__visuals_style_presets[
                'input_colourspace_visual'].next_style())

        return True

    def toggle_correlate_colourspace_visual_visibility_action(self):
        for visual in self.__correlate_colourspace_visual.children:
            visual.visible = not visual.visible

        return True

    def cycle_correlate_colourspace_visual_style_action(self):
        self.__detach_correlate_colourspace_visual()

        self.__attach_correlate_colourspace_visual(
            self.__visuals_style_presets[
                'correlate_colourspace_visual'].next_style())

        return True

    def toggle_spectral_locus_visual_visibility_action(self):
        self.__spectral_locus_visual.visible = (
            not self.__spectral_locus_visual.visible)

    def cycle_spectral_locus_visual_style_action(self):
        # TODO: Implement definition.
        self.__detach_spectral_locus_visual()

        self.__attach_spectral_locus_visual()

        return True

    def toggle_RGB_scatter_visual_visibility_action(self):
        self.__RGB_scatter_visual.visible = (
            not self.__RGB_scatter_visual.visible)

        return True

    def cycle_RGB_scatter_visual_style_action(self):
        self.__detach_RGB_scatter_visual()

        self.__attach_RGB_scatter_visual(self.__create_RGB_scatter_image())

        self.update()

        return True

    def toggle_pointer_gamut_visual_visibility_action(self):
        # TODO: Implement definition.

        self.__pointer_gamut_visual.visible = (
            not self.__pointer_gamut_visual.visible)

        return True

    def cycle_pointer_gamut_visual_style_action(self):
        # TODO: Implement definition.

        self.__pointer_gamut_visual.remove_parent(self.scene)

        return True

    def cycle_correlate_colourspace_action(self):
        self.__detach_correlate_colourspace_visual()

        self.__attach_correlate_colourspace_visual(
            self.__visuals_style_presets[
                'correlate_colourspace_visual'].current_style())

        return True

    def cycle_reference_colourspace_action(self):
        self.__detach_camera()
        self.__store_visuals_visibility()
        self.__detach_visuals()
        self.__attach_visuals()
        self.__restore_visuals_visibility()
        self.__attach_camera()

        return True

    def toggle_axis_visual_visibility_action(self):
        self.__axis_visual.visible = (
            not self.__axis_visual.visible)

        return True

    def toggle_blacks_clamp_action(self):
        self.__clamp_blacks = not self.__clamp_blacks

        self.__store_visuals_visibility()
        self.__detach_visuals()
        self.__attach_visuals()
        self.__restore_visuals_visibility()

        return True

    def toggle_whites_clamp_action(self):
        self.__clamp_whites = not self.__clamp_whites

        self.__store_visuals_visibility()
        self.__detach_visuals()
        self.__attach_visuals()
        self.__restore_visuals_visibility()

        return True
