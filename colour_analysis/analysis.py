# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import json
import numpy as np
import os
from collections import OrderedDict, namedtuple
from itertools import cycle

from vispy.scene import SceneCanvas
from vispy.scene.cameras import PanZoomCamera, TurntableCamera

from colour import RGB_COLOURSPACES, read_image

from colour_analysis.common import REFERENCE_COLOURSPACES
from colour_analysis.constants import DEFAULT_IMAGE, SETTINGS_FILE
from colour_analysis.visuals import (
    RGB_colourspace_gamut_visual,
    RGB_scatter_visual,
    axis_visual,
    image_visual,
    spectral_locus_visual)


Sequence = namedtuple('Sequence', ('modifiers', 'key'))

Action = namedtuple('Action', ('name', 'description', 'sequence'))

RGB_colourspace_gamut_visual_style = namedtuple(
    'RGB_colourspace_gamut_visual_style',
    ('name',
     'description',
     'uniform_colour',
     'uniform_opacity',
     'wireframe',
     'wireframe_colour',
     'wireframe_opacity'))

GamutViewCamera = namedtuple(
    'GamutViewCamera',
    ('name',
     'description',
     'reference_colourspace',
     'fov',
     'elevation',
     'azimuth',
     'distance',
     'center',
     'up'))


class Styles(object):
    def __init__(self, styles):
        self.__styles = styles
        self.__indexes = np.arange(len(styles))

    def current_style(self):
        return self.__styles[self.__indexes[0]]

    def next_style(self):
        self.__indexes = np.roll(self.__indexes, -1)

        return self.current_style()


class Analysis(SceneCanvas):
    def __init__(self,
                 image_path=DEFAULT_IMAGE,
                 input_colourspace='Rec. 709',
                 input_oecf='Rec. 709',
                 input_linear=True,
                 reference_colourspace='CIE xyY',
                 correlate_colourspace='ACEScg',
                 settings=None):
        SceneCanvas.__init__(self,
                             keys='interactive',
                             title="Colour - Analysis")

        self.__image_path = None
        self.image_path = image_path
        self.__input_colourspace = None
        self.input_colourspace = input_colourspace
        self.__input_oecf = None
        self.input_oecf = input_oecf
        self.__input_linear = None
        self.input_linear = input_linear
        self.__reference_colourspace = None
        self.reference_colourspace = reference_colourspace
        self.__correlate_colourspace = None
        self.correlate_colourspace = correlate_colourspace
        self.__settings = (json.load(open(SETTINGS_FILE))
                           if settings is None else
                           settings)

        self.__actions_settings = {}
        self.__styles_settings = {}
        self.__cameras_settings = {}

        self.__image = None
        self.image = np.random.random((256, 256, 3))

        self.__clamp_blacks = False
        self.__clamp_whites = True

        self.__grid = None
        self.__gamut_view = None
        self.__diagram_view = None
        self.__image_view = None

        self.__input_colourspace_visual = None
        self.__correlate_colourspace_visual = None
        self.__spectral_locus_visual = None
        self.__RGB_scatter_visual = None
        self.__pointer_gamut_visual = None
        self.__axis_visual = None

        self.__image_visual = None

        self.__gamut_view_visuals_visibility = None

        self.__RGB_colourspaces_cycle = cycle(
            [c for c in sorted(RGB_COLOURSPACES)
             if c not in ('aces', 'adobe1998', 'prophoto')])

        self.__initialise_actions_settings()
        self.__initialise_styles_settings()
        self.__initialise_cameras_settings()

        self.initialise_image()
        self.initialise_views()
        self.initialise_visuals()
        self.initialise_cameras()

        self.show()

    @property
    def image_path(self):
        """
        Property for **self.__image_path** private attribute.

        Returns
        -------
        unicode
            self.__image_path.
        """

        return self.__image_path

    @image_path.setter
    def image_path(self, value):
        """
        Setter for **self.__image_path** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert os.path.exists(value), (
                '"{0}" input image doesn\'t exists!'.format(value))
        self.__image_path = value

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
    def input_oecf(self):
        """
        Property for **self.__input_oecf** private attribute.

        Returns
        -------
        unicode
            self.__input_oecf.
        """

        return self.__input_oecf

    @input_oecf.setter
    def input_oecf(self, value):
        """
        Setter for **self.__input_oecf** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert type(value) in (str, unicode), (
                ('"{0}" attribute: "{1}" type is not '
                 '"str" or "unicode"!').format('input_oecf', value))
            assert value in RGB_COLOURSPACES, (
                '"{0}" OECF is not associated with any factory '
                'RGB colourspaces: "{1}".').format(value, ', '.join(
                sorted(RGB_COLOURSPACES.keys())))
        self.__input_oecf = value

    @property
    def input_linear(self):
        """
        Property for **self.__input_linear** private attribute.

        Returns
        -------
        bool
            self.__input_linear.
        """

        return self.__input_linear

    @input_linear.setter
    def input_linear(self, value):
        """
        Setter for **self.__input_linear** private attribute.

        Parameters
        ----------
        value : bool
            Attribute value.
        """

        if value is not None:
            assert type(value) is bool, (
                '"{0}" attribute: "{1}" type is not "bool"!'.format(
                    'input_linear', value))

        self.__input_linear = value

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

        raise AttributeError(
            '"{0}" attribute is read only!'.format('settings'))

    def __initialise_actions_settings(self):
        self.__actions_settings = {}

        for name, action in self.__settings.get('actions', ()).items():
            if action.get('sequence') is not None:
                sequence = Sequence(
                    modifiers=action.get('sequence').get('modifiers', ()),
                    key=action.get('sequence').get('key'))
            else:
                sequence = Sequence(modifiers=(), key=None)

            self.__actions_settings[name] = Action(
                name=action.get('name'),
                description=action.get('description'),
                sequence=sequence)

    def __initialise_styles_settings(self):
        self.__styles_settings = OrderedDict()

        for visual, styles in self.__settings.get('styles', ()).items():
            self.__styles_settings[visual] = []

            for style in styles:
                self.__styles_settings[visual].append(
                    RGB_colourspace_gamut_visual_style(
                        name=style.get('name'),
                        description=style.get('description'),
                        uniform_colour=style.get('uniform_colour'),
                        uniform_opacity=style.get('uniform_opacity'),
                        wireframe=style.get('wireframe'),
                        wireframe_colour=style.get('wireframe_colour'),
                        wireframe_opacity=style.get('wireframe_opacity')))

            self.__styles_settings[visual] = Styles(
                self.__styles_settings[visual])

    def __initialise_cameras_settings(self):
        self.__cameras_settings = {}

        for view, cameras in self.__settings.get('cameras', ()).items():
            if view == 'gamut_view':
                self.__cameras_settings['gamut_view'] = {}

                for camera in cameras.values():
                    self.__cameras_settings[view][camera.get(
                        'reference_colourspace')] = GamutViewCamera(
                        name=camera.get('name'),
                        description=camera.get('description'),
                        reference_colourspace=camera.get(
                            'reference_colourspace'),
                        fov=camera.get('fov'),
                        elevation=camera.get('elevation'),
                        azimuth=camera.get('azimuth'),
                        distance=camera.get('distance'),
                        center=camera.get('center'),
                        up=camera.get('up'))

    def __create_RGB_scatter_image(self):
        image = self.__image

        if self.__clamp_blacks:
            image = np.clip(image, 0, np.inf)

        if self.__clamp_whites:
            image = np.clip(image, -np.inf, 1)

        return image

    def __create_image_view_image(self):
        colourspace = RGB_COLOURSPACES[self.__input_oecf]

        return colourspace.transfer_function(self.__image)

    def __create_colourspace_visual(self, style, colourspace=None):
        return RGB_colourspace_gamut_visual(
            colourspace=colourspace,
            reference_colourspace=self.__reference_colourspace,
            uniform_colour=style.uniform_colour,
            uniform_opacity=style.uniform_opacity,
            wireframe=style.wireframe,
            wireframe_colour=style.wireframe_colour,
            wireframe_opacity=style.wireframe_opacity,
            parent=self.__gamut_view.scene)

    def __attach_input_colourspace_visual(self,
                                          style,
                                          colourspace=None):
        colourspace = (self.__input_colourspace
                       if colourspace is None else
                       colourspace)

        self.__input_colourspace_visual = (
            self.__create_colourspace_visual(style, colourspace))

    def __detach_input_colourspace_visual(self):
        self.__input_colourspace_visual.remove_parent(self.__gamut_view.scene)

    def __attach_correlate_colourspace_visual(self,
                                              style,
                                              colourspace=None):
        colourspace = (self.__correlate_colourspace
                       if colourspace is None else
                       colourspace)

        self.__correlate_colourspace_visual = (
            self.__create_colourspace_visual(style, colourspace))

    def __detach_correlate_colourspace_visual(self):
        self.__correlate_colourspace_visual.remove_parent(
            self.__gamut_view.scene)

    def __attach_RGB_scatter_visual(self, RGB):
        self.__RGB_scatter_visual = RGB_scatter_visual(
            RGB,
            reference_colourspace=self.__reference_colourspace,
            parent=self.__gamut_view)

    def __detach_RGB_scatter_visual(self):
        self.__RGB_scatter_visual.remove_parent(
            self.__gamut_view.scene)

    def __attach_spectral_locus_visual(self):
        self.__spectral_locus_visual = spectral_locus_visual(
            reference_colourspace=self.__reference_colourspace,
            parent=self.__gamut_view.scene)

    def __detach_spectral_locus_visual(self):
        self.__spectral_locus_visual.remove_parent(self.__gamut_view.scene)

    def __attach_axis_visual(self):
        self.__axis_visual = axis_visual(parent=self.__gamut_view.scene)

    def __detach_axis_visual(self):
        self.__axis_visual.remove_parent(self.__gamut_view.scene)

    def __attach_gamut_view_visuals(self):
        self.__attach_RGB_scatter_visual(self.__create_RGB_scatter_image())

        self.__attach_input_colourspace_visual(
            self.__styles_settings['input_colourspace_visual'].current_style())

        self.__attach_correlate_colourspace_visual(
            self.__styles_settings[
                'correlate_colourspace_visual'].current_style())

        self.__attach_spectral_locus_visual()

        self.__attach_axis_visual()

    def __detach_gamut_view_visuals(self):
        self.__detach_RGB_scatter_visual()

        self.__detach_input_colourspace_visual()

        self.__detach_correlate_colourspace_visual()

        self.__detach_spectral_locus_visual()

        self.__detach_axis_visual()

    def __attach_image_view_visuals(self):
        self.__image_visual = image_visual(
            self.__create_image_view_image(),
            parent=self.__image_view.scene)

    def __detach_image_view_visuals(self):
        self.__image_visual.remove_parent(self.__image_view.scene)

    def __store_gamut_view_visuals_visibility(self):
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

        print(visible)
        self.__gamut_view_visuals_visibility = visible

    def __restore_gamut_view_visuals_visibility(self):
        visible = self.__gamut_view_visuals_visibility

        self.__RGB_scatter_visual.visible = visible['RGB_scatter_visual']
        for visual in self.__input_colourspace_visual.children:
            visual.visible = visible['input_colourspace_visual']
        for visual in self.__correlate_colourspace_visual.children:
            visual.visible = visible['correlate_colourspace_visual']
        self.__spectral_locus_visual.visible = (
            visible['spectral_locus_visual'])
        self.__axis_visual.visible = visible['axis_visual']

    def initialise_image(self):
        image = read_image(self.__image_path)
        if not self.__input_linear:
            colourspace = RGB_COLOURSPACES[self.__input_oecf]
            image = colourspace.inverse_transfer_function(image)

        self.__image = image

        return True

    def initialise_views(self):
        self.__grid = self.central_widget.add_grid()

        self.__gamut_view = self.__grid.add_view(row=0, col=0, col_span=2)
        self.__gamut_view.border_color = (0.5, 0.5, 0.5, 1)

        self.__diagram_view = self.__grid.add_view(row=1, col=0)
        self.__diagram_view.border_color = (0.5, 0.5, 0.5, 1)

        self.__image_view = self.__grid.add_view(row=1, col=1)
        self.__image_view.border_color = (0.5, 0.5, 0.5, 1)

        return True

    def initialise_visuals(self):
        self.__attach_gamut_view_visuals()

        self.__attach_image_view_visuals()

        return True

    def initialise_cameras(self):
        camera_settings = self.__cameras_settings['gamut_view'][
            self.__reference_colourspace]

        self.__gamut_view.camera = TurntableCamera(
            fov=camera_settings.fov,
            elevation=camera_settings.elevation,
            azimuth=camera_settings.azimuth,
            distance=camera_settings.distance,
            center=camera_settings.center,
            up=camera_settings.up)

        self.__diagram_view.camera = PanZoomCamera(aspect=1)
        self.__image_view.camera.flip = (False, True, False)

        self.__image_view.camera = PanZoomCamera(aspect=1)
        self.__image_view.camera.flip = (False, True, False)

        return True

    def toggle_input_colourspace_visual_visibility_action(self):
        for visual in self.__input_colourspace_visual.children:
            visual.visible = not visual.visible

        return True

    def cycle_input_colourspace_visual_style_action(self):
        self.__detach_input_colourspace_visual()

        self.__attach_input_colourspace_visual(
            self.__styles_settings['input_colourspace_visual'].next_style())

        return True

    def toggle_correlate_colourspace_visual_visibility_action(self):
        for visual in self.__correlate_colourspace_visual.children:
            visual.visible = not visual.visible

        return True

    def cycle_correlate_colourspace_visual_style_action(self):
        self.__detach_correlate_colourspace_visual()

        self.__attach_correlate_colourspace_visual(
            self.__styles_settings[
                'correlate_colourspace_visual'].next_style())

        return True

    def cycle_correlate_colourspace_visual_colourspace_action(self):
        self.__detach_correlate_colourspace_visual()

        self.__attach_correlate_colourspace_visual(
            self.__styles_settings[
                'correlate_colourspace_visual'].current_style(),
            next(self.__RGB_colourspaces_cycle))

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

        self.__pointer_gamut_visual.remove_parent(self.__gamut_view.scene)

        self.update()

        return True

    def toggle_axis_visual_visibility_action(self):
        self.__axis_visual.visible = (
            not self.__axis_visual.visible)

        return True

    def fit_image_visual_image_action(self):
        # TODO: Implement definition.

        print('fit_image_visual_image')

        return True

    def toggle_blacks_clamp_action(self):
        self.__clamp_blacks = not self.__clamp_blacks

        self.__store_gamut_view_visuals_visibility()

        self.__detach_gamut_view_visuals()

        self.__attach_gamut_view_visuals()

        self.__restore_gamut_view_visuals_visibility()

        return True

    def toggle_whites_clamp_action(self):
        self.__clamp_whites = not self.__clamp_whites

        self.__store_gamut_view_visuals_visibility()

        self.__detach_gamut_view_visuals()

        self.__attach_gamut_view_visuals()

        self.__restore_gamut_view_visuals_visibility()

        return True

    def on_key_press(self, event):
        key = event.key.name
        modifiers = sorted([modifier.name for modifier in event.modifiers])
        for action in self.__actions_settings.values():
            if (key == action.sequence.key and
                        modifiers == sorted(action.sequence.modifiers)):
                getattr(self, '{0}_action'.format(action.name))()
