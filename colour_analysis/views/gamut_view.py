#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gamut View
==========

Defines the *Gamut View* related objects:

-   :class:`GamutView`
"""

from __future__ import division, unicode_literals

from collections import OrderedDict, namedtuple

import numpy as np
from vispy.scene.visuals import Text
from vispy.scene.widgets.viewbox import ViewBox
from colour import RGB_COLOURSPACES

from colour_analysis.cameras import OrbitCamera
from colour_analysis.constants import REFERENCE_COLOURSPACES
from colour_analysis.utilities import Cycle
from colour_analysis.visuals import (
    RGB_colourspace_volume_visual,
    RGB_scatter_visual,
    axis_visual,
    spectral_locus_visual,
    pointer_gamut_visual,
    pointer_gamut_hull_visual)

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013 - 2015 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['CameraPreset',
           'RGB_colourspaceVisualPreset',
           'AxisPreset',
           'GamutView']

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
     'depth_value',
     'center',
     'up'))
"""
Defines a camera settings preset.

CameraPreset : namedtuple
"""

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
"""
Defines a *RGB* colourspace volume visual style preset.

RGB_colourspaceVisualPreset : namedtuple
"""

AxisPreset = namedtuple(
    'AxisPreset',
    ('name',
     'description',
     'reference_colourspace',
     'scale'))
"""
Defines an axis visual style preset.

AxisPreset : namedtuple
"""


class GamutView(ViewBox):
    """
    Defines the *Gamut View*.

    Parameters
    ----------
    scene_canvas : SceneCanvas, optional
        Current `vispy.scene.SceneCanvas` instance.
    image : array_like, optional
        Image to use in the view interactions.
    input_colourspace : unicode, optional
        {'Rec. 709', 'ACES2065-1', 'ACEScc', 'ACEScg', 'ACESproxy',
        'ALEXA Wide Gamut RGB', 'Adobe RGB 1998', 'Adobe Wide Gamut RGB',
        'Apple RGB', 'Best RGB', 'Beta RGB', 'CIE RGB', 'Cinema Gamut',
        'ColorMatch RGB', 'DCI-P3', 'DCI-P3+', 'DRAGONcolor', 'DRAGONcolor2',
        'Don RGB 4', 'ECI RGB v2', 'Ekta Space PS 5', 'Max RGB', 'NTSC RGB',
        'Pal/Secam RGB', 'ProPhoto RGB', 'REDcolor', 'REDcolor2', 'REDcolor3',
        'REDcolor4', 'Rec. 2020', 'Russell RGB', 'S-Gamut', 'S-Gamut3',
        'S-Gamut3.Cine', 'SMPTE-C RGB', 'V-Gamut', 'Xtreme RGB', 'aces',
        'adobe1998', 'prophoto', 'sRGB'}

        :class:`colour.RGB_Colourspace` class instance name defining `image`
        argument colourspace.
    reference_colourspace : unicode, optional
        {'CIE XYZ', 'CIE xyY', 'CIE Lab', 'CIE Luv', 'CIE UCS', 'CIE UVW',
        'IPT'}

        Reference colourspace to use for colour conversions / transformations.
    correlate_colourspace : unicode, optional
        See `input_colourspace` argument for possible values, default value is
        *ACEScg*.

        :class:`colour.RGB_Colourspace` class instance name defining the
        comparison / correlate colourspace.
    \*\*kwargs : \*\*, optional
        Keywords arguments passed to
        :class:`vispy.scene.widgets.viewbox.Viewbox` class constructor.

    Attributes
    ----------
    scene_canvas
    image
    input_colourspace
    reference_colourspace
    correlate_colourspace
    settings

    Methods
    -------
    toggle_input_colourspace_visual_visibility_action
    cycle_input_colourspace_visual_style_action
    toggle_correlate_colourspace_visual_visibility_action
    cycle_correlate_colourspace_visual_style_action
    toggle_RGB_scatter_visual_visibility_action
    cycle_RGB_scatter_visual_style_action
    toggle_pointer_gamut_visual_visibility_action
    cycle_pointer_gamut_visual_style_action
    toggle_spectral_locus_visual_visibility_action
    cycle_spectral_locus_visual_style_action
    toggle_axis_visual_visibility_action
    decrease_colourspace_visual_resolution_action
    increase_colourspace_visual_resolution_action
    """

    def __init__(self,
                 scene_canvas=None,
                 image=None,
                 input_colourspace='Rec. 709',
                 reference_colourspace='CIE xyY',
                 correlate_colourspace='ACEScg',
                 settings=None,
                 **kwargs):
        self.__initialised = False

        ViewBox.__init__(self, **kwargs)

        self.unfreeze()

        self.__scene_canvas = scene_canvas

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

        self.__title_overlay_visual = None

        self.__colourspace_visual_resolution = 16
        self.__colourspace_visual_resolution_limits = (1, 64)

        self.__input_colourspace_visual = None
        self.__correlate_colourspace_visual = None
        self.__RGB_scatter_visual = None
        self.__pointer_gamut_visual = None
        self.__pointer_gamut_hull_visual = None
        self.__spectral_locus_visual = None
        self.__axis_visual = None

        self.__visuals = ('RGB_scatter_visual',
                          'input_colourspace_visual',
                          'correlate_colourspace_visual',
                          'pointer_gamut_visual',
                          'pointer_gamut_hull_visual',
                          'spectral_locus_visual',
                          'axis_visual')

        self.__visuals_visibility = None

        self.__create_presets()

        self.__create_visuals()
        self.__attach_visuals()
        self.__create_camera()

        self.__create_title_overlay_visual()
        self.__scene_canvas.events.resize.connect(
            self.__scene_canvas_resize_event)

        self.__initialised = True

    @property
    def scene_canvas(self):
        """
        Property for **self.scene_canvas** attribute.

        Returns
        -------
        SceneCanvas
        """

        return self.__scene_canvas

    @scene_canvas.setter
    def scene_canvas(self, value):
        """
        Setter for **self.scene_canvas** attribute.

        Parameters
        ----------
        value : SceneCanvas
            Attribute value.
        """

        raise AttributeError('"{0}" attribute is read only!'.format(
            'scene_canvas'))

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

        if self.__initialised:
            self.__store_visuals_visibility()
            self.__detach_visuals()
            self.__create_RGB_scatter_visual(self.__image)
            self.__attach_visuals()
            self.__restore_visuals_visibility()
            self.__title_overlay_visual_text()

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

        if self.__initialised:
            self.__detach_visuals()
            self.__create_input_colourspace_visual(
                self.__visuals_style_presets[
                    'input_colourspace_visual'].current_item())
            self.__attach_visuals()
            self.__title_overlay_visual_text()

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

        if self.__initialised:
            self.__store_visuals_visibility()
            self.__detach_visuals()
            self.__create_visuals()
            self.__attach_visuals()
            self.__restore_visuals_visibility()
            self.__create_camera()
            self.__title_overlay_visual_text()

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

        if self.__initialised:
            self.__detach_visuals()
            self.__create_correlate_colourspace_visual(
                self.__visuals_style_presets[
                    'correlate_colourspace_visual'].current_item())
            self.__attach_visuals()
            self.__title_overlay_visual_text()

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
        """
        Creates the camera presets using :attr:`GamutView.settings` attribute
        value.
        """

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
                    depth_value=camera['depth_value'],
                    center=camera['center'],
                    up=camera['up']))

    def __create_visuals_style_presets(self):
        """
        Creates the visuals style presets using :attr:`GamutView.settings`
        attribute value.
        """

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

            self.__visuals_style_presets[visual] = Cycle(
                self.__visuals_style_presets[visual])

    def __create_axis_presets(self):
        """
        Creates the axis style presets using :attr:`GamutView.settings`
        attribute value.
        """

        for axis in self.__settings['axis'].values():
            self.__axis_presets[axis['reference_colourspace']] = (
                AxisPreset(
                    name=axis['name'],
                    description=axis['description'],
                    reference_colourspace=axis['reference_colourspace'],
                    scale=axis['scale']))

    def __create_presets(self):
        """
        Creates the view presets.
        """

        self.__create_camera_presets()
        self.__create_visuals_style_presets()
        self.__create_axis_presets()

    def __create_RGB_colourspace_visual(self, colourspace, style):
        """
        Creates a *RGB* colourspace volume visual with given colourspace and
        style.

        Parameters
        ----------
        colourspace : unicode
            {'Rec. 709', 'ACES2065-1', 'ACEScc', 'ACEScg', 'ACESproxy',
            'ALEXA Wide Gamut RGB', 'Adobe RGB 1998', 'Adobe Wide Gamut RGB',
            'Apple RGB', 'Best RGB', 'Beta RGB', 'CIE RGB', 'Cinema Gamut',
            'ColorMatch RGB', 'DCI-P3', 'DCI-P3+', 'DRAGONcolor', 'DRAGONcolor2',
            'Don RGB 4', 'ECI RGB v2', 'Ekta Space PS 5', 'Max RGB', 'NTSC RGB',
            'Pal/Secam RGB', 'ProPhoto RGB', 'REDcolor', 'REDcolor2', 'REDcolor3',
            'REDcolor4', 'Rec. 2020', 'Russell RGB', 'S-Gamut', 'S-Gamut3',
            'S-Gamut3.Cine', 'SMPTE-C RGB', 'V-Gamut', 'Xtreme RGB', 'aces',
            'adobe1998', 'prophoto', 'sRGB'}

            :class:`colour.RGB_Colourspace` class instance name defining the
            colourspace the visual will be using.
        style : RGB_colourspaceVisualPreset
            *RGB* colourspace volume visual style.

        Returns
        -------
        RGB_colourspace_volume_visual
            *RGB* colourspace volume visual.
        """

        return RGB_colourspace_volume_visual(
            colourspace=colourspace,
            reference_colourspace=self.__reference_colourspace,
            segments=self.__colourspace_visual_resolution,
            uniform_colour=style.uniform_colour,
            uniform_opacity=style.uniform_opacity,
            wireframe=style.wireframe,
            wireframe_colour=style.wireframe_colour,
            wireframe_opacity=style.wireframe_opacity)

    def __create_input_colourspace_visual(self, style=None):
        """
        Creates the input colourspace visual according to
        :attr:`DiagramView.input_colourspace` attribute value and given style.

        Parameters
        ----------
        style : RGB_colourspaceVisualPreset
            *RGB* colourspace volume visual style.
        """

        style = (self.__visuals_style_presets[
                     'input_colourspace_visual'].current_item()
                 if style is None else
                 style)

        self.__input_colourspace_visual = (
            self.__create_RGB_colourspace_visual(
                self.__input_colourspace, style))

    def __create_correlate_colourspace_visual(self, style=None):
        """
        Creates the correlate colourspace visual according to
        :attr:`DiagramView.correlate_colourspace` attribute value and given
        style.

        Parameters
        ----------
        style : RGB_colourspaceVisualPreset
            *RGB* colourspace volume visual style.
        """

        style = (self.__visuals_style_presets[
                     'correlate_colourspace_visual'].current_item()
                 if style is None else
                 style)

        self.__correlate_colourspace_visual = (
            self.__create_RGB_colourspace_visual(
                self.__correlate_colourspace, style))

    def __create_RGB_scatter_visual(self, RGB=None):
        """
        Creates the *RGB* scatter visual for given *RGB* array according to
        :attr:`GamutView.__reference_colourspace` attribute value.

        Parameters
        ----------
        RGB : array_like, optional
            *RGB* array to draw.
        """

        RGB = self.__image if RGB is None else RGB

        self.__RGB_scatter_visual = RGB_scatter_visual(
            RGB, reference_colourspace=self.__reference_colourspace)

    def __create_pointer_gamut_visual(self):
        """
        Creates the *Pointer's Gamut* visual according to
        :attr:`GamutView.__reference_colourspace` attribute value.
        """

        self.__pointer_gamut_visual = pointer_gamut_visual(
            reference_colourspace=self.__reference_colourspace)

    def __create_pointer_gamut_hull_visual(self):
        """
        Creates the *Pointer's Gamut* hull visual according to
        :attr:`GamutView.__reference_colourspace` attribute value.
        """

        self.__pointer_gamut_hull_visual = pointer_gamut_hull_visual(
            reference_colourspace=self.__reference_colourspace)

    def __create_spectral_locus_visual(self):
        """
        Creates the spectral locus visual according to
        :attr:`GamutView.__reference_colourspace` attribute value.
        """

        self.__spectral_locus_visual = spectral_locus_visual(
            reference_colourspace=self.__reference_colourspace)

    def __create_axis_visual(self):
        """
        Creates the axis visual.
        """

        self.__axis_visual = axis_visual(
            scale=self.__axis_presets[self.__reference_colourspace].scale)

    def __create_visuals(self):
        """
        Creates the *Gamut View* visuals.
        """

        for visual in self.__visuals:
            visual = '_GamutView__create_{0}'.format(visual)
            getattr(self, visual)()

    def __create_camera(self):
        """
        Creates the *Gamut View* camera.
        """

        speed_factor = 10 / np.max(np.abs(
            self.__RGB_scatter_visual._data['a_position']))

        camera_settings = self.__camera_presets[self.__reference_colourspace]

        self.camera = OrbitCamera(
            fov=camera_settings.fov,
            elevation=camera_settings.elevation,
            azimuth=camera_settings.azimuth,
            distance=camera_settings.distance,
            translate_speed=camera_settings.translate_speed * speed_factor,
            center=camera_settings.center,
            up=camera_settings.up)

        self.camera.depth_value = camera_settings.depth_value

    def __attach_visuals(self):
        """
        Attaches / parents the visuals to the *Gamut View* scene.
        """

        for visual in self.__visuals:
            visual = '_GamutView__{0}'.format(visual)
            getattr(self, visual).parent = self.scene

    def __detach_visuals(self):
        """
        Detaches / un-parents the visuals from the *Gamut View* scene.
        """

        for visual in self.__visuals:
            visual = '_GamutView__{0}'.format(visual)
            getattr(self, visual).parent = None

    def __store_visuals_visibility(self):
        """
        Stores visuals visibility in :attr:`GamutView.__visuals_visibility`
        attribute.
        """

        visibility = OrderedDict()
        for visual in self.__visuals:
            visibility[visual] = (
                getattr(self, '_GamutView__{0}'.format(visual)).visible)

        self.__visuals_visibility = visibility

    def __restore_visuals_visibility(self):
        """
        Restores visuals visibility from :attr:`GamutView.__visuals_visibility`
        attribute.
        """

        visibility = self.__visuals_visibility
        for visual in self.__visuals:
            getattr(self, '_GamutView__{0}'.format(visual)).visible = (
                visibility[visual])

    def __create_title_overlay_visual(self):
        """
        Creates the title overlay visual.
        """

        self.__title_overlay_visual = Text(str(),
                                           anchor_x='center',
                                           anchor_y='bottom',
                                           font_size=10,
                                           color=(0.8, 0.8, 0.8),
                                           parent=self)

        self.__title_overlay_visual_position()
        self.__title_overlay_visual_text()

    def __title_overlay_visual_position(self):
        """
        Sets the title overlay visual position.
        """

        self.__title_overlay_visual.pos = self.size[0] / 2, 32

    def __title_overlay_visual_text(self):
        """
        Sets the title overlay visual text.
        """

        title = ''

        if self.__input_colourspace_visual.children[0].visible:
            title += self.__input_colourspace
            title += ' - '
        if self.__correlate_colourspace_visual.children[0].visible:
            title += self.__correlate_colourspace
            title += ' - '

        title += self.__reference_colourspace

        if self.__scene_canvas.clamp_blacks:
            title += ' - '
            title += 'Blacks Clamped'

        if self.__scene_canvas.clamp_whites:
            title += ' - '
            title += 'Whites Clamped'

        self.__title_overlay_visual.text = title

    def __scene_canvas_resize_event(self, event=None):
        """
        Slot for current :class:`vispy.scene.SceneCanvas` instance resize
        event.

        Parameters
        ----------
        event : Object
            Event.
        """

        self.__title_overlay_visual_position()

    def toggle_input_colourspace_visual_visibility_action(self):
        """
        Defines the slot triggered by the
        *toggle_input_colourspace_visual_visibility* action.

        Returns
        -------
        bool
            Definition success.
        """

        self.__input_colourspace_visual.visible = (
            not self.__input_colourspace_visual.visible)
        self.__title_overlay_visual_text()

        return True

    def cycle_input_colourspace_visual_style_action(self):
        """
        Defines the slot triggered by the
        *cycle_input_colourspace_visual_style* action.

        Returns
        -------
        bool
            Definition success.
        """

        self.__detach_visuals()
        self.__create_input_colourspace_visual(
            self.__visuals_style_presets[
                'input_colourspace_visual'].next_item())
        self.__attach_visuals()

        return True

    def toggle_correlate_colourspace_visual_visibility_action(self):
        """
        Defines the slot triggered by the
        *toggle_correlate_colourspace_visual_visibility* action.

        Returns
        -------
        bool
            Definition success.
        """

        self.__correlate_colourspace_visual.visible = (
            not self.__correlate_colourspace_visual.visible)
        self.__title_overlay_visual_text()

        return True

    def cycle_correlate_colourspace_visual_style_action(self):
        """
        Defines the slot triggered by the
        *cycle_correlate_colourspace_visual_style* action.

        Returns
        -------
        bool
            Definition success.
        """

        self.__detach_visuals()
        self.__create_correlate_colourspace_visual(
            self.__visuals_style_presets[
                'correlate_colourspace_visual'].next_item())
        self.__attach_visuals()

        return True

    def toggle_RGB_scatter_visual_visibility_action(self):
        """
        Defines the slot triggered by the
        *toggle_RGB_scatter_visual_visibility* action.

        Returns
        -------
        bool
            Definition success.
        """

        self.__RGB_scatter_visual.visible = (
            not self.__RGB_scatter_visual.visible)

        return True

    def cycle_RGB_scatter_visual_style_action(self):
        """
        Defines the slot triggered by the
        *cycle_RGB_scatter_visual_style* action.

        Returns
        -------
        bool
            Definition success.
        """

        self.__detach_visuals()
        self.__create_RGB_scatter_visual(self.__image)
        self.__attach_visuals()

        return True

    def toggle_pointer_gamut_visual_visibility_action(self):
        """
        Defines the slot triggered by the
        *toggle_pointer_gamut_visual_visibility* action.

        Returns
        -------
        bool
            Definition success.
        """

        self.__pointer_gamut_visual.visible = (
            not self.__pointer_gamut_visual.visible)
        self.__pointer_gamut_hull_visual.visible = (
            not self.__pointer_gamut_hull_visual.visible)

        return True

    def cycle_pointer_gamut_visual_style_action(self):
        """
        Defines the slot triggered by the *cycle_pointer_gamut_visual_style*
        action.

        Returns
        -------
        bool
            Definition success.
        """

        self.__detach_visuals()
        self.__create_pointer_gamut_visual()
        self.__attach_visuals()

        return True

    def toggle_spectral_locus_visual_visibility_action(self):
        """
        Defines the slot triggered by the
        *toggle_spectral_locus_visual_visibility* action.

        Returns
        -------
        bool
            Definition success.
        """

        self.__spectral_locus_visual.visible = (
            not self.__spectral_locus_visual.visible)

        return True

    def cycle_spectral_locus_visual_style_action(self):
        """
        Defines the slot triggered by the *cycle_spectral_locus_visual_style*
        action.

        Returns
        -------
        bool
            Definition success.
        """

        self.__detach_visuals()
        self.__create_spectral_locus_visual()
        self.__attach_visuals()

        return True

    def toggle_axis_visual_visibility_action(self):
        """
        Defines the slot triggered by the *toggle_axis_visual_visibility*
        action.

        Returns
        -------
        bool
            Definition success.
        """

        self.__axis_visual.visible = (
            not self.__axis_visual.visible)

        return True

    def decrease_colourspace_visual_resolution_action(self):
        """
        Defines the slot triggered by the
        *decrease_colourspace_visual_resolution*
        action.

        Returns
        -------
        bool
            Definition success.
        """

        self.__colourspace_visual_resolution -= 2
        self.__colourspace_visual_resolution = max(
            self.__colourspace_visual_resolution_limits[0],
            self.__colourspace_visual_resolution)
        self.__store_visuals_visibility()
        self.__detach_visuals()
        self.__create_input_colourspace_visual()
        self.__create_correlate_colourspace_visual()
        self.__attach_visuals()
        self.__restore_visuals_visibility()

    def increase_colourspace_visual_resolution_action(self):
        """
        Defines the slot triggered by the
        *increase_colourspace_visual_resolution*
        action.

        Returns
        -------
        bool
            Definition success.
        """

        self.__colourspace_visual_resolution += 2
        self.__colourspace_visual_resolution = min(
            self.__colourspace_visual_resolution_limits[1],
            self.__colourspace_visual_resolution)
        self.__store_visuals_visibility()
        self.__detach_visuals()
        self.__create_input_colourspace_visual()
        self.__create_correlate_colourspace_visual()
        self.__attach_visuals()
        self.__restore_visuals_visibility()
