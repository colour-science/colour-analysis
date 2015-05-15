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
     'uniform_colour',
     'uniform_opacity',
     'wireframe',
     'wireframe_colour',
     'wireframe_opacity'))


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
                 image_path,
                 input_colourspace,
                 input_oecf,
                 reference_colourspace,
                 correlate_colourspace,
                 settings=None):
        SceneCanvas.__init__(self,
                             keys='interactive',
                             title="Colour - Analysis")

        self.__image_path = None
        self.image_path = image_path or DEFAULT_IMAGE
        self.__input_colourspace = None
        self.input_colourspace = input_colourspace
        self.__input_oecf = None
        self.input_oecf = input_oecf
        self.__reference_colourspace = None
        self.reference_colourspace = reference_colourspace
        self.__correlate_colourspace = None
        self.correlate_colourspace = correlate_colourspace
        self.__settings = (json.load(open(SETTINGS_FILE))
                           if settings is None else
                           settings)
        self.__actions = {}
        self.__styles = {}

        self.__image = None
        # self.image = read_image(image_path)

        import skimage.data

        self.image = skimage.data.lena() / 255

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

        self.__RGB_colourspaces_cycle = cycle(
            [c for c in sorted(RGB_COLOURSPACES)
             if c not in ('aces', 'adobe1998', 'prophoto')])

        self.initialise_actions()
        self.initialise_styles()

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

    def __colourspace_visual_initialise(self, style, colourspace=None):
        return RGB_colourspace_gamut_visual(
            colourspace=colourspace,
            reference_colourspace=self.__reference_colourspace,
            uniform_colour=style.uniform_colour,
            uniform_opacity=style.uniform_opacity,
            wireframe=style.wireframe,
            wireframe_colour=style.wireframe_colour,
            wireframe_opacity=style.wireframe_opacity,
            parent=self.__gamut_view.scene)

    def __input_colourspace_visual_initialise(self,
                                              style,
                                              colourspace=None):
        colourspace = (self.__input_colourspace
                       if colourspace is None else
                       colourspace)

        self.__input_colourspace_visual = (
            self.__colourspace_visual_initialise(style, colourspace))

    def __correlate_colourspace_visual_initialise(self,
                                                  style,
                                                  colourspace=None):
        colourspace = (self.__correlate_colourspace
                       if colourspace is None else
                       colourspace)

        self.__correlate_colourspace_visual = (
            self.__colourspace_visual_initialise(style, colourspace))

    def initialise_views(self):
        self.__grid = self.central_widget.add_grid()

        self.__gamut_view = self.__grid.add_view(row=0, col=0, col_span=2)
        self.__gamut_view.border_color = (0.5, 0.5, 0.5, 1)

        self.__diagram_view = self.__grid.add_view(row=1, col=0)
        self.__diagram_view.border_color = (0.5, 0.5, 0.5, 1)

        self.__image_view = self.__grid.add_view(row=1, col=1)
        self.__image_view.border_color = (0.5, 0.5, 0.5, 1)

    def initialise_visuals(self):
        # Gamut View.
        self.__RGB_scatter_visual = RGB_scatter_visual(
            self.__image,
            reference_colourspace=self.__reference_colourspace,
            parent=self.__gamut_view)

        self.__input_colourspace_visual_initialise(
            self.__styles['input_colourspace_visual'].current_style())

        self.__correlate_colourspace_visual_initialise(
            self.__styles['correlate_colourspace_visual'].current_style())

        self.__spectral_locus_visual = spectral_locus_visual(
            reference_colourspace=self.__reference_colourspace,
            parent=self.__gamut_view.scene)

        self.__axis_visual = axis_visual(parent=self.__gamut_view.scene)

        # Diagram View.

        # Image View.
        self.__image_visual = image_visual(self.__image,
                                           parent=self.__image_view.scene)

    def initialise_cameras(self):
        self.__gamut_view.camera = TurntableCamera(fov=45, up='+z')

        self.__diagram_view.camera = PanZoomCamera(aspect=1)
        self.__image_view.camera.flip = (False, True, False)

        self.__image_view.camera = PanZoomCamera(aspect=1)
        self.__image_view.camera.flip = (False, True, False)

    def initialise_actions(self):
        self.__actions = {}
        for key, value in self.__settings.get('actions', ()).items():
            if value.get('sequence') is not None:
                sequence = Sequence(
                    modifiers=value.get('sequence').get('modifiers', ()),
                    key=value.get('sequence').get('key'))
            else:
                sequence = Sequence(modifiers=(), key=None)

            self.__actions[key] = Action(
                name=value.get('name'),
                description=value.get('description'),
                sequence=sequence)

    def initialise_styles(self):
        self.__styles = OrderedDict()
        for key, value in self.__settings.get('styles', ()).items():
            self.__styles[key] = []
            for style in value:
                self.__styles[key].append(RGB_colourspace_gamut_visual_style(
                    name=style.get('name'),
                    uniform_colour=style.get('uniform_colour'),
                    uniform_opacity=style.get('uniform_opacity'),
                    wireframe=style.get('wireframe'),
                    wireframe_colour=style.get('wireframe_colour'),
                    wireframe_opacity=style.get('wireframe_opacity')))
            self.__styles[key] = Styles(self.__styles[key])

    def toggle_input_colourspace_visual_visibility_action(self):
        for visual in self.__input_colourspace_visual.children:
            visual.visible = not visual.visible

    def cycle_input_colourspace_visual_style_action(self):
        self.__input_colourspace_visual.remove_parent(self.__gamut_view.scene)

        self.__input_colourspace_visual_initialise(
            self.__styles['input_colourspace_visual'].next_style())

        self.update()

    def toggle_correlate_colourspace_visual_visibility_action(self):
        for visual in self.__correlate_colourspace_visual.children:
            visual.visible = not visual.visible

    def cycle_correlate_colourspace_visual_style_action(self):
        self.__correlate_colourspace_visual.remove_parent(
            self.__gamut_view.scene)

        self.__correlate_colourspace_visual_initialise(
            self.__styles['correlate_colourspace_visual'].next_style())

        self.update()

    def cycle_correlate_colourspace_visual_colourspace_action(self):
        self.__correlate_colourspace_visual.remove_parent(
            self.__gamut_view.scene)

        self.__correlate_colourspace_visual_initialise(
            self.__styles['correlate_colourspace_visual'].current_style(),
            next(self.__RGB_colourspaces_cycle))

        self.update()

    def toggle_spectral_locus_visual_visibility_action(self):
        self.__spectral_locus_visual.visible = (
            not self.__spectral_locus_visual.visible)

    def cycle_spectral_locus_visual_style_action(self):
        self.__spectral_locus_visual.remove_parent(self.__gamut_view.scene)

        self.update()

    def toggle_RGB_scatter_visual_visibility_action(self):
        self.__RGB_scatter_visual.visible = (
            not self.__RGB_scatter_visual.visible)

    def cycle_RGB_scatter_visual_style_action(self):
        self.__RGB_scatter_visual.remove_parent(self.__gamut_view.scene)

        self.update()

    def toggle_pointer_gamut_visual_visibility_action(self):
        self.__pointer_gamut_visual.visible = (
            not self.__pointer_gamut_visual.visible)

    def cycle_pointer_gamut_visual_style_action(self):
        self.__pointer_gamut_visual.remove_parent(self.__gamut_view.scene)

        self.update()

    def toggle_axis_visual_visibility_action(self):
        self.__axis_visual.visible = (
            not self.__axis_visual.visible)

    def fit_image_visual_image_action(self):
        print('fit_image_visual_image')

    def on_key_press(self, event):
        key = event.key.name
        modifiers = sorted([modifier.name for modifier in event.modifiers])
        for action in self.__actions.values():
            if (key == action.sequence.key and
                        modifiers == sorted(action.sequence.modifiers)):
                getattr(self, '{0}_action'.format(action.name))()
