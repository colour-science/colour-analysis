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
from vispy.scene.widgets import Label, ViewBox, Widget
from vispy.scene.visuals import GridLines

from colour import RGB_COLOURSPACES
from colour.utilities import is_string

from colour_analysis.cameras import OrbitCamera
from colour_analysis.constants import REFERENCE_COLOURSPACES
from colour_analysis.utilities import Cycle
from colour_analysis.visuals import (
    RGB_colourspace_volume_visual, RGB_scatter_visual, axis_visual,
    spectral_locus_visual, pointer_gamut_visual, pointer_gamut_hull_visual)

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013-2021 - Colour Developers'
__license__ = 'New BSD License - https://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-developers@colour-science.org'
__status__ = 'Production'

__all__ = [
    'CameraPreset', 'RGB_ColourspaceVisualPreset', 'GridVisualPreset',
    'AxisPreset', 'GamutView'
]

CameraPreset = namedtuple(
    'CameraPreset',
    ('name', 'description', 'reference_colourspace', 'fov', 'elevation',
     'azimuth', 'distance', 'translate_speed', 'depth_value', 'center', 'up'))
"""
Defines a camera settings preset.

CameraPreset : namedtuple
"""

RGB_ColourspaceVisualPreset = namedtuple(
    'RGB_ColourspaceVisualPreset',
    ('name', 'description', 'segments', 'uniform_colour', 'uniform_opacity',
     'wireframe', 'wireframe_colour', 'wireframe_opacity'))
"""
Defines a *RGB* colourspace volume visual style preset.

RGB_ColourspaceVisualPreset : namedtuple
"""

GridVisualPreset = namedtuple('GridVisualPreset',
                              ('name', 'description', 'uniform_colour'))
"""
Defines a grid visual style preset.

GridVisualPreset : namedtuple
"""

AxisPreset = namedtuple(
    'AxisPreset', ('name', 'description', 'reference_colourspace', 'scale'))
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
        **{'ITU-R BT.709', 'ACES2065-1', 'ACEScc', 'ACEScg', 'ACESproxy',
        'ALEXA Wide Gamut', 'Adobe RGB (1998)', 'Adobe Wide Gamut RGB',
        'Apple RGB', 'Best RGB', 'Beta RGB', 'CIE RGB', 'Cinema Gamut',
        'ColorMatch RGB', 'DCI-P3', 'DCI-P3+', 'DRAGONcolor', 'DRAGONcolor2',
        'Don RGB 4', 'ECI RGB v2', 'ERIMM RGB', 'Ekta Space PS 5', 'Max RGB',
        'NTSC', 'Pal/Secam', 'ProPhoto RGB', 'REDcolor', 'REDcolor2',
        'REDcolor3', 'REDcolor4', 'RIMM RGB', 'ROMM RGB', 'ITU-R BT.2020',
        'Russell RGB', 'S-Gamut', 'S-Gamut3', 'S-Gamut3.Cine', 'SMPTE-C RGB',
        'V-Gamut', 'Xtreme RGB', 'sRGB'}**,
        :class:`colour.RGB_Colourspace` class instance name defining `image`
        argument colourspace.
    reference_colourspace : unicode, optional
        **{'CIE XYZ', 'CIE xyY', 'CIE Lab', 'CIE Luv', 'CIE UCS', 'CIE UVW',
        'IPT', 'Hunter Lab', 'Hunter Rdab'}**,
        Reference colourspace to use for colour conversions / transformations.
    correlate_colourspace : unicode, optional
        See `input_colourspace` argument for possible values, default value is
        *ACEScg*.

        :class:`colour.RGB_Colourspace` class instance name defining the
        comparison / correlate colourspace.

    Other Parameters
    ----------------
    \\**kwargs : dict, optional
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
                 input_colourspace='ITU-R BT.709',
                 reference_colourspace='CIE xyY',
                 correlate_colourspace='ACEScg',
                 settings=None,
                 **kwargs):
        self._initialised = False

        ViewBox.__init__(self, **kwargs)

        self.unfreeze()

        self._scene_canvas = scene_canvas

        self._image = None
        self.image = image
        self._input_colourspace = None
        self.input_colourspace = input_colourspace
        self._reference_colourspace = None
        self.reference_colourspace = reference_colourspace
        self._correlate_colourspace = None
        self.correlate_colourspace = correlate_colourspace

        self._settings = None
        self.settings = settings

        self._camera_presets = {}
        self._visuals_style_presets = OrderedDict()
        self._axis_presets = {}

        self._grid = None

        self._label = None

        self._colourspace_visual_resolution = 16
        self._colourspace_visual_resolution_limits = (1, 64)

        self._input_colourspace_visual = None
        self._correlate_colourspace_visual = None
        self._RGB_scatter_visual = None
        self._pointer_gamut_visual = None
        self._pointer_gamut_hull_visual = None
        self._spectral_locus_visual = None
        self._grid_visual = None
        self._axis_visual = None

        self._visuals = ('RGB_scatter_visual', 'input_colourspace_visual',
                         'correlate_colourspace_visual',
                         'pointer_gamut_visual', 'pointer_gamut_hull_visual',
                         'spectral_locus_visual', 'grid_visual', 'axis_visual')

        self._visuals_visibility = None

        self._create_presets()

        self._create_visuals()
        self._attach_visuals()
        self._create_camera()

        self._create_label()

        self._initialised = True

    @property
    def scene_canvas(self):
        """
        Property for **self.scene_canvas** attribute.

        Returns
        -------
        SceneCanvas
        """

        return self._scene_canvas

    @property
    def image(self):
        """
        Property for **self._image** private attribute.

        Returns
        -------
        array_like
            self._image.
        """

        return self._image

    @image.setter
    def image(self, value):
        """
        Setter for **self._image** private attribute.

        Parameters
        ----------
        value : array_like
            Attribute value.
        """

        if value is not None:
            assert isinstance(value, (tuple, list, np.ndarray, np.matrix)), ((
                '"{0}" attribute: "{1}" is not a "tuple", "list", "ndarray" '
                'or "matrix" instance!').format('image', value))

        self._image = value

        if self._initialised:
            self._store_visuals_visibility()
            self._detach_visuals()
            self._create_RGB_scatter_visual(self._image)
            self._attach_visuals()
            self._restore_visuals_visibility()
            self._label_text()

    @property
    def input_colourspace(self):
        """
        Property for **self._input_colourspace** private attribute.

        Returns
        -------
        unicode
            self._input_colourspace.
        """

        return self._input_colourspace

    @input_colourspace.setter
    def input_colourspace(self, value):
        """
        Setter for **self._input_colourspace** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert is_string(value), (('"{0}" attribute: "{1}" is not a '
                                       '"string" like object!').format(
                                           'input_colourspace', value))
            assert value in RGB_COLOURSPACES, (
                '"{0}" colourspace not found in factory RGB colourspaces: '
                '"{1}".').format(value, ', '.join(
                    sorted(RGB_COLOURSPACES.keys())))

        self._input_colourspace = value

        if self._initialised:
            self._detach_visuals()
            self._create_input_colourspace_visual(self._visuals_style_presets[
                'input_colourspace_visual'].current_item())
            self._attach_visuals()
            self._label_text()

    @property
    def reference_colourspace(self):
        """
        Property for **self._reference_colourspace** private attribute.

        Returns
        -------
        unicode
            self._reference_colourspace.
        """

        return self._reference_colourspace

    @reference_colourspace.setter
    def reference_colourspace(self, value):
        """
        Setter for **self._reference_colourspace** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert is_string(value), (('"{0}" attribute: "{1}" is not a '
                                       '"string" like object!').format(
                                           'reference_colourspace', value))
            assert value in REFERENCE_COLOURSPACES, (
                '"{0}" reference colourspace not found in factory reference '
                'colourspaces: "{1}".').format(value, ', '.join(
                    sorted(REFERENCE_COLOURSPACES.keys())))

        self._reference_colourspace = value

        if self._initialised:
            self._store_visuals_visibility()
            self._detach_visuals()
            self._create_visuals()
            self._attach_visuals()
            self._restore_visuals_visibility()
            self._create_camera()
            self._label_text()

    @property
    def correlate_colourspace(self):
        """
        Property for **self._correlate_colourspace** private attribute.

        Returns
        -------
        unicode
            self._correlate_colourspace.
        """

        return self._correlate_colourspace

    @correlate_colourspace.setter
    def correlate_colourspace(self, value):
        """
        Setter for **self._correlate_colourspace** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert is_string(value), (('"{0}" attribute: "{1}" is not a '
                                       '"string" like object!').format(
                                           'correlate_colourspace', value))
            assert value in RGB_COLOURSPACES, (
                '"{0}" colourspace not found in factory RGB colourspaces: '
                '"{1}".').format(value, ', '.join(
                    sorted(RGB_COLOURSPACES.keys())))

        self._correlate_colourspace = value

        if self._initialised:
            self._detach_visuals()
            self._create_correlate_colourspace_visual(
                self._visuals_style_presets[
                    'correlate_colourspace_visual'].current_item())
            self._attach_visuals()
            self._label_text()

    @property
    def settings(self):
        """
        Property for **self._settings** private attribute.

        Returns
        -------
        dict
            self._settings.
        """

        return self._settings

    @settings.setter
    def settings(self, value):
        """
        Setter for **self._settings** private attribute.

        Parameters
        ----------
        value : dict
            Attribute value.
        """

        if value is not None:
            assert isinstance(value, dict), (
                '"{0}" attribute: "{1}" is not a "dict" instance!'.format(
                    'settings', value))
        self._settings = value

    def _create_camera_presets(self):
        """
        Creates the camera presets using :attr:`GamutView.settings` attribute
        value.
        """

        for camera in self._settings['cameras']['gamut_view'].values():
            self._camera_presets[camera['reference_colourspace']] = (
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

    def _create_visuals_style_presets(self):
        """
        Creates the visuals style presets using :attr:`GamutView.settings`
        attribute value.
        """

        for visual, styles in self._settings['styles']['gamut_view'].items():
            self._visuals_style_presets[visual] = []

            for style in styles:
                if visual in ('input_colourspace_visual',
                              'correlate_colourspace_visual'):
                    self._visuals_style_presets[style['visual']].append(
                        RGB_ColourspaceVisualPreset(
                            name=style['name'],
                            description=style['description'],
                            segments=style['segments'],
                            uniform_colour=style['uniform_colour'],
                            uniform_opacity=style['uniform_opacity'],
                            wireframe=style['wireframe'],
                            wireframe_colour=style['wireframe_colour'],
                            wireframe_opacity=style['wireframe_opacity']))
                elif visual in 'grid_visual':
                    self._visuals_style_presets[style['visual']].append(
                        GridVisualPreset(
                            name=style['name'],
                            description=style['description'],
                            uniform_colour=style['uniform_colour']))

            self._visuals_style_presets[visual] = Cycle(
                self._visuals_style_presets[visual])

    def _create_axis_presets(self):
        """
        Creates the axis style presets using :attr:`GamutView.settings`
        attribute value.
        """

        for axis in self._settings['axis'].values():
            self._axis_presets[axis['reference_colourspace']] = (AxisPreset(
                name=axis['name'],
                description=axis['description'],
                reference_colourspace=axis['reference_colourspace'],
                scale=axis['scale']))

    def _create_presets(self):
        """
        Creates the view presets.
        """

        self._create_camera_presets()
        self._create_visuals_style_presets()
        self._create_axis_presets()

    def _create_grid_visual(self, style=None):
        """
        Creates the grid visual.

        Parameters
        ----------
        style : GridVisualPreset
            Grid visual style.
        """

        style = (self._visuals_style_presets['grid_visual'].current_item()
                 if style is None else style)

        self._grid_visual = GridLines(color=style.uniform_colour)

    def _create_RGB_colourspace_visual(self, colourspace, style):
        """
        Creates a *RGB* colourspace volume visual with given colourspace and
        style.

        Parameters
        ----------
        colourspace : unicode
            **{'ITU-R BT.709', 'ACES2065-1', 'ACEScc', 'ACEScg', 'ACESproxy',
            'ALEXA Wide Gamut', 'Adobe RGB (1998)', 'Adobe Wide Gamut RGB',
            'Apple RGB', 'Best RGB', 'Beta RGB', 'CIE RGB', 'Cinema Gamut',
            'ColorMatch RGB', 'DCI-P3', 'DCI-P3+', 'DRAGONcolor',
            'DRAGONcolor2', 'Don RGB 4', 'ECI RGB v2', 'ERIMM RGB',
            'Ekta Space PS 5', 'Max RGB', 'NTSC', 'Pal/Secam',
            'ProPhoto RGB', 'REDcolor', 'REDcolor2', 'REDcolor3', 'REDcolor4',
            'RIMM RGB', 'ROMM RGB', 'ITU-R BT.2020', 'Russell RGB', 'S-Gamut',
            'S-Gamut3', 'S-Gamut3.Cine', 'SMPTE-C RGB', 'V-Gamut',
            'Xtreme RGB', 'sRGB'}**,
            :class:`colour.RGB_Colourspace` class instance name defining the
            colourspace the visual will be using.
        style : RGB_ColourspaceVisualPreset
            *RGB* colourspace volume visual style.

        Returns
        -------
        RGB_colourspace_volume_visual
            *RGB* colourspace volume visual.
        """

        return RGB_colourspace_volume_visual(
            colourspace=colourspace,
            reference_colourspace=self._reference_colourspace,
            segments=self._colourspace_visual_resolution,
            uniform_colour=style.uniform_colour,
            uniform_opacity=style.uniform_opacity,
            wireframe=style.wireframe,
            wireframe_colour=style.wireframe_colour,
            wireframe_opacity=style.wireframe_opacity)

    def _create_input_colourspace_visual(self, style=None):
        """
        Creates the input colourspace visual according to
        :attr:`DiagramView.input_colourspace` attribute value and given style.

        Parameters
        ----------
        style : RGB_ColourspaceVisualPreset
            *RGB* colourspace volume visual style.
        """

        style = (self._visuals_style_presets['input_colourspace_visual']
                 .current_item() if style is None else style)

        self._input_colourspace_visual = (self._create_RGB_colourspace_visual(
            self._input_colourspace, style))

    def _create_correlate_colourspace_visual(self, style=None):
        """
        Creates the correlate colourspace visual according to
        :attr:`DiagramView.correlate_colourspace` attribute value and given
        style.

        Parameters
        ----------
        style : RGB_ColourspaceVisualPreset
            *RGB* colourspace volume visual style.
        """

        style = (self._visuals_style_presets['correlate_colourspace_visual']
                 .current_item() if style is None else style)

        self._correlate_colourspace_visual = (
            self._create_RGB_colourspace_visual(self._correlate_colourspace,
                                                style))

    def _create_RGB_scatter_visual(self, RGB=None):
        """
        Creates the *RGB* scatter visual for given *RGB* array according to
        :attr:`GamutView._reference_colourspace` attribute value.

        Parameters
        ----------
        RGB : array_like, optional
            *RGB* array to draw.
        """

        RGB = self._image if RGB is None else RGB

        self._RGB_scatter_visual = RGB_scatter_visual(
            RGB, reference_colourspace=self._reference_colourspace)

    def _create_pointer_gamut_visual(self):
        """
        Creates the *Pointer's Gamut* visual according to
        :attr:`GamutView._reference_colourspace` attribute value.
        """

        self._pointer_gamut_visual = pointer_gamut_visual(
            reference_colourspace=self._reference_colourspace)

    def _create_pointer_gamut_hull_visual(self):
        """
        Creates the *Pointer's Gamut* hull visual according to
        :attr:`GamutView._reference_colourspace` attribute value.
        """

        self._pointer_gamut_hull_visual = pointer_gamut_hull_visual(
            reference_colourspace=self._reference_colourspace)

    def _create_spectral_locus_visual(self):
        """
        Creates the spectral locus visual according to
        :attr:`GamutView._reference_colourspace` attribute value.
        """

        self._spectral_locus_visual = spectral_locus_visual(
            reference_colourspace=self._reference_colourspace)

    def _create_axis_visual(self):
        """
        Creates the axis visual.
        """

        self._axis_visual = axis_visual(
            scale=self._axis_presets[self._reference_colourspace].scale)

    def _create_visuals(self):
        """
        Creates the *Gamut View* visuals.
        """

        for visual in self._visuals:
            visual = '_create_{0}'.format(visual)
            getattr(self, visual)()

    def _create_camera(self):
        """
        Creates the *Gamut View* camera.
        """

        speed_factor = 10 / np.max(
            np.abs(self._RGB_scatter_visual._data['a_position']))

        camera_settings = self._camera_presets[self._reference_colourspace]

        self.camera = OrbitCamera(
            fov=camera_settings.fov,
            elevation=camera_settings.elevation,
            azimuth=camera_settings.azimuth,
            distance=camera_settings.distance,
            translate_speed=camera_settings.translate_speed * speed_factor,
            center=camera_settings.center,
            up=camera_settings.up)

        self.camera.depth_value = camera_settings.depth_value

    def _attach_visuals(self):
        """
        Attaches / parents the visuals to the *Gamut View* scene.
        """

        for visual in self._visuals:
            visual = '_{0}'.format(visual)
            getattr(self, visual).parent = self.scene

    def _detach_visuals(self):
        """
        Detaches / un-parents the visuals from the *Gamut View* scene.
        """

        for visual in self._visuals:
            visual = '_{0}'.format(visual)
            getattr(self, visual).parent = None

    def _store_visuals_visibility(self):
        """
        Stores visuals visibility in :attr:`GamutView._visuals_visibility`
        attribute.
        """

        visibility = OrderedDict()
        for visual in self._visuals:
            visibility[visual] = getattr(self, '_{0}'.format(visual)).visible

        self._visuals_visibility = visibility

    def _restore_visuals_visibility(self):
        """
        Restores visuals visibility from :attr:`GamutView._visuals_visibility`
        attribute.
        """

        visibility = self._visuals_visibility
        for visual in self._visuals:
            getattr(self, '_{0}'.format(visual)).visible = (visibility[visual])

    def _create_label(self):
        """
        Creates the label.
        """

        self._label = Label(str(), color=(0.8, 0.8, 0.8))
        self._label.stretch = (1, 0.1)
        self._grid = self.add_grid(margin=16)
        self._grid.add_widget(self._label, row=0, col=0)
        self._grid.add_widget(Widget(), row=1, col=0)

        self._label_text()

    def _label_text(self):
        """
        Sets the label text.
        """

        title = ''

        if self._input_colourspace_visual.children[0].visible:
            title += self._input_colourspace
            title += ' - '
        if self._correlate_colourspace_visual.children[0].visible:
            title += self._correlate_colourspace
            title += ' - '

        title += self._reference_colourspace

        if self._scene_canvas.clamp_blacks:
            title += ' - '
            title += 'Blacks Clamped'

        if self._scene_canvas.clamp_whites:
            title += ' - '
            title += 'Whites Clamped'

        self._label.text = title

    def toggle_input_colourspace_visual_visibility_action(self):
        """
        Defines the slot triggered by the
        *toggle_input_colourspace_visual_visibility* action.

        Returns
        -------
        bool
            Definition success.
        """

        self._input_colourspace_visual.visible = (
            not self._input_colourspace_visual.visible)
        self._label_text()

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

        self._detach_visuals()
        self._create_input_colourspace_visual(self._visuals_style_presets[
            'input_colourspace_visual'].next_item())
        self._attach_visuals()

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

        self._correlate_colourspace_visual.visible = (
            not self._correlate_colourspace_visual.visible)
        self._label_text()

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

        self._detach_visuals()
        self._create_correlate_colourspace_visual(self._visuals_style_presets[
            'correlate_colourspace_visual'].next_item())
        self._attach_visuals()

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

        self._RGB_scatter_visual.visible = (
            not self._RGB_scatter_visual.visible)

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

        self._detach_visuals()
        self._create_RGB_scatter_visual(self._image)
        self._attach_visuals()

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

        self._pointer_gamut_visual.visible = (
            not self._pointer_gamut_visual.visible)
        self._pointer_gamut_hull_visual.visible = (
            not self._pointer_gamut_hull_visual.visible)

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

        self._detach_visuals()
        self._create_pointer_gamut_visual()
        self._attach_visuals()

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

        self._spectral_locus_visual.visible = (
            not self._spectral_locus_visual.visible)

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

        self._detach_visuals()
        self._create_spectral_locus_visual()
        self._attach_visuals()

        return True

    def toggle_grid_visual_visibility_action(self):
        """
        Defines the slot triggered by the *toggle_grid_visual_visibility*
        action.

        Returns
        -------
        bool
            Definition success.
        """

        self._grid_visual.visible = not self._grid_visual.visible

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

        self._axis_visual.visible = (not self._axis_visual.visible)

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

        self._colourspace_visual_resolution -= 2
        self._colourspace_visual_resolution = max(
            self._colourspace_visual_resolution_limits[0],
            self._colourspace_visual_resolution)
        self._store_visuals_visibility()
        self._detach_visuals()
        self._create_input_colourspace_visual()
        self._create_correlate_colourspace_visual()
        self._attach_visuals()
        self._restore_visuals_visibility()

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

        self._colourspace_visual_resolution += 2
        self._colourspace_visual_resolution = min(
            self._colourspace_visual_resolution_limits[1],
            self._colourspace_visual_resolution)
        self._store_visuals_visibility()
        self._detach_visuals()
        self._create_input_colourspace_visual()
        self._create_correlate_colourspace_visual()
        self._attach_visuals()
        self._restore_visuals_visibility()
