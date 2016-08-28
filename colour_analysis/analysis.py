# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Colour Analysis
===============

Defines *Colour - Analysis* main class:

-   :class:`ColourAnalysis`
"""

from __future__ import division, unicode_literals

import json
import os
from collections import OrderedDict, deque, namedtuple
from itertools import cycle

import numpy as np
from vispy.scene import SceneCanvas

from colour import RGB_COLOURSPACES, is_string

from colour_analysis import __application_name__, __version__
from colour_analysis.constants import (
    DEFAULT_FAILSAFE_IMAGE,
    SETTINGS_FILE,
    REFERENCE_COLOURSPACES)
from colour_analysis.views import (
    ConsoleView,
    DiagramView,
    GamutView,
    ImageView)

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013-2016 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['Sequence',
           'Action',
           'ViewPreset',
           'LayoutPreset',
           'ColourAnalysis']

Sequence = namedtuple(
    'Sequence',
    ('modifiers',
     'key'))
"""
Defines a modifier and key keyboard sequence.

Sequence : namedtuple
"""

Action = namedtuple(
    'Action',
    ('name',
     'description',
     'sequence'))
"""
Defines a user action / interaction associated with a :class:`Sequence`.

Actions are name bound to methods affixed with *_action* in
:class:`ColourAnalysis` or its children views. For example an action
named *toggle_blacks_clamp* will be bound to available
*toggle_blacks_clamp_action* methods in :class:`ColourAnalysis` or its children
views.

Action : namedtuple
"""

ViewPreset = namedtuple(
    'ViewPreset',
    ('name',
     'description',
     'view',
     'row',
     'column',
     'row_span',
     'column_span'))
"""
Defines a view preset used with :class:`LayoutPreset` describing the location
of the view in the layout grid.

ViewPreset : namedtuple
"""

LayoutPreset = namedtuple(
    'LayoutPreset',
    ('name',
     'description',
     'views'))
"""
Defines a layout preset describing which views are added to the
:class:`ColourAnalysis` class.

LayoutPreset : namedtuple
"""


class ColourAnalysis(SceneCanvas):
    """
    Defines *Colour - Analysis* canvas, a class inheriting from
    :class:`vispy.scene.SceneCanvas`.

    Parameters
    ----------
    image : array_like, optional
        Image to analyse.
    image_path : unicode, optional
        Image path.
    input_colourspace : unicode, optional
        **{'Rec. 709', 'ACES2065-1', 'ACEScc', 'ACEScg', 'ACESproxy',
        'ALEXA Wide Gamut RGB', 'Adobe RGB (1998)', 'Adobe Wide Gamut RGB',
        'Apple RGB', 'Best RGB', 'Beta RGB', 'CIE RGB', 'Cinema Gamut',
        'ColorMatch RGB', 'DCI-P3', 'DCI-P3+', 'DRAGONcolor', 'DRAGONcolor2',
        'Don RGB 4', 'ECI RGB v2', 'ERIMM RGB', 'Ekta Space PS 5', 'Max RGB',
        'NTSC RGB', 'Pal/Secam RGB', 'ProPhoto RGB', 'REDcolor', 'REDcolor2',
        'REDcolor3', 'REDcolor4', 'RIMM RGB', 'ROMM RGB', 'Rec. 2020',
        'Russell RGB', 'S-Gamut', 'S-Gamut3', 'S-Gamut3.Cine', 'SMPTE-C RGB',
        'V-Gamut', 'Xtreme RGB', 'sRGB'}**,
        :class:`colour.RGB_Colourspace` class instance name defining `image`
        argument colourspace.
    input_oecf : unicode, optional
        See `input_colourspace` argument for possible values.

        :class:`colour.RGB_Colourspace` class instance name defining the image
        opto-electronic transfer function.
    input_linear : bool, optional
        Is input image linear.
    reference_colourspace : unicode, optional
        **{'CIE XYZ', 'CIE xyY', 'CIE Lab', 'CIE Luv', 'CIE UCS', 'CIE UVW',
        'IPT', 'Hunter Lab', 'Hunter Rdab'}**,
        Reference colourspace to use for colour conversions / transformations.
    correlate_colourspace : unicode, optional
        See `input_colourspace` argument for possible values, default value is
        *ACEScg*.

        :class:`colour.RGB_Colourspace` class instance name defining the
        comparison / correlate colourspace.
    settings : dict, optional
        Settings for the :class:`ColourAnalysis` class and its children views.
    layout : unicode, optional
        Layout the :class:`ColourAnalysis` class will use.

    Attributes
    ----------
    image
    image_path
    input_colourspace
    input_oecf
    input_linear
    reference_colourspace
    correlate_colourspace
    settings
    layout
    actions
    console_view
    gamut_view
    image_view
    diagram_view
    clamp_blacks
    clamp_whites

    Methods
    -------
    on_key_press
    cycle_correlate_colourspace_action
    cycle_reference_colourspace_action
    toggle_blacks_clamp_action
    toggle_whites_clamp_action
    """

    def __init__(self,
                 image=None,
                 image_path=None,
                 input_colourspace='Rec. 709',
                 input_oecf='Rec. 709',
                 input_linear=True,
                 reference_colourspace='CIE xyY',
                 correlate_colourspace='ACEScg',
                 settings=None,
                 layout='layout_1'):
        self._initialised = False

        title = '{0} - {1}'.format(__application_name__, __version__)

        SceneCanvas.__init__(
            self,
            keys='interactive',
            title=('{0} - {1}'.format(title, image_path)
                   if image_path is not None
                   else title),
            size=settings['scene_canvas']['size'],
            bgcolor=settings['scene_canvas']['scene_canvas_background_colour'],
            config={'samples': settings['scene_canvas']['samples']})

        self.unfreeze()

        self._image = None
        self.image = image if image is not None else DEFAULT_FAILSAFE_IMAGE
        self._image_path = None
        self.image_path = image_path
        self._input_colourspace = None
        self.input_colourspace = input_colourspace
        self._input_oecf = None
        self.input_oecf = input_oecf
        self._input_linear = None
        self.input_linear = input_linear
        self._reference_colourspace = None
        self.reference_colourspace = reference_colourspace
        self._correlate_colourspace = None
        self.correlate_colourspace = correlate_colourspace
        self._settings = (json.load(open(SETTINGS_FILE))
                          if settings is None else
                          settings)
        self._layout = None
        self.layout = layout

        self._clamp_blacks = False
        self._clamp_whites = False

        self._layout_presets = OrderedDict()
        self._actions = {}

        self._console_view = None
        self._gamut_view = None
        self._image_view = None
        self._diagram_view = None
        self._views = None

        self._grid = None

        self._RGB_colourspaces_cycle = cycle(
            [c for c in sorted(RGB_COLOURSPACES)
             if c not in ('aces', 'adobe1998', 'prophoto')])

        reference_colourspaces_deque = deque(REFERENCE_COLOURSPACES)
        reference_colourspaces_deque.rotate(-REFERENCE_COLOURSPACES.index(
            self._reference_colourspace) - 1)
        self._reference_colourspaces_cycle = cycle(
            reference_colourspaces_deque)

        self._create_layout_presets()
        self._create_actions()
        self._create_views()
        self._layout_views()

        self.show()

        self._initialised = True

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
            assert isinstance(value, (tuple, list, np.ndarray, np.matrix)), (
                ('"{0}" attribute: "{1}" is not a "tuple", "list", "ndarray" '
                 'or "matrix" instance!').format('image', value))

        self._image = value

        if self._initialised:
            image = self._create_image()

            for view in self._views:
                if hasattr(view, 'image'):
                    view.image = image

    @property
    def image_path(self):
        """
        Property for **self._image_path** private attribute.

        Returns
        -------
        unicode
            self._image_path.
        """

        return self._image_path

    @image_path.setter
    def image_path(self, value):
        """
        Setter for **self._image_path** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert is_string(value), (
                ('"{0}" attribute: "{1}" is not a '
                 '"string" like object!').format('image_path', value))
            assert os.path.exists(value), (
                '"{0}" input image doesn\'t exists!'.format(value))
        self._image_path = value

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
            assert is_string(value), (
                ('"{0}" attribute: "{1}" is not a '
                 '"string" like object!').format('input_colourspace', value))
            assert value in RGB_COLOURSPACES, (
                '"{0}" colourspace not found in factory RGB colourspaces: '
                '"{1}".').format(
                value, ', '.join(sorted(RGB_COLOURSPACES.keys())))
        self._input_colourspace = value

    @property
    def input_oecf(self):
        """
        Property for **self._input_oecf** private attribute.

        Returns
        -------
        unicode
            self._input_oecf.
        """

        return self._input_oecf

    @input_oecf.setter
    def input_oecf(self, value):
        """
        Setter for **self._input_oecf** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert is_string(value), (
                ('"{0}" attribute: "{1}" is not a '
                 '"string" like object!').format('input_oecf', value))
            assert value in RGB_COLOURSPACES, (
                '"{0}" OECF is not associated with any factory '
                'RGB colourspaces: "{1}".').format(value, ', '.join(
                sorted(RGB_COLOURSPACES.keys())))
        self._input_oecf = value

    @property
    def input_linear(self):
        """
        Property for **self._input_linear** private attribute.

        Returns
        -------
        bool
            self._input_linear.
        """

        return self._input_linear

    @input_linear.setter
    def input_linear(self, value):
        """
        Setter for **self._input_linear** private attribute.

        Parameters
        ----------
        value : bool
            Attribute value.
        """

        if value is not None:
            assert isinstance(value, bool), (
                '"{0}" attribute: "{1}" is not a "bool" instance!'.format(
                    'input_linear', value))
        self._input_linear = value

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
            assert is_string(value), (
                ('"{0}" attribute: "{1}" is not a '
                 '"string" like object!').format(
                    'reference_colourspace', value))
            assert value in REFERENCE_COLOURSPACES, (
                '"{0}" reference colourspace not found in factory reference '
                'colourspaces: "{1}".').format(
                value, ', '.join(sorted(REFERENCE_COLOURSPACES.keys())))
        self._reference_colourspace = value

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
            assert is_string(value), (
                ('"{0}" attribute: "{1}" is not a '
                 '"string" like object!').format(
                    'correlate_colourspace', value))
            assert value in RGB_COLOURSPACES, (
                '"{0}" colourspace not found in factory RGB colourspaces: '
                '"{1}".').format(value, ', '.join(
                sorted(RGB_COLOURSPACES.keys())))
        self._correlate_colourspace = value

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

        raise AttributeError(
            '"{0}" attribute is read only!'.format('settings'))

    @property
    def layout(self):
        """
        Property for **self._layout** private attribute.

        Returns
        -------
        unicode
            self._layout.
        """

        return self._layout

    @layout.setter
    def layout(self, value):
        """
        Setter for **self._layout** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert is_string(value), (
                ('"{0}" attribute: "{1}" is not a '
                 '"string" like object!').format('layout', value))
        self._layout = value

    @property
    def actions(self):
        """
        Property for **self._actions** private attribute.

        Returns
        -------
        dict
            self._actions.
        """

        return self._actions

    @actions.setter
    def actions(self, value):
        """
        Setter for **self._actions** private attribute.

        Parameters
        ----------
        value : dict
            Attribute value.
        """

        raise AttributeError(
            '"{0}" attribute is read only!'.format('actions'))

    @property
    def console_view(self):
        """
        Property for **self.console_view** attribute.

        Returns
        -------
        ViewBox
        """

        return self._console_view

    @console_view.setter
    def console_view(self, value):
        """
        Setter for **self.console_view** attribute.

        Parameters
        ----------
        value : ViewBox
            Attribute value.
        """

        raise AttributeError(
            '"{0}" attribute is read only!'.format('console_view'))

    @property
    def gamut_view(self):
        """
        Property for **self.gamut_view** attribute.

        Returns
        -------
        ViewBox
        """

        return self._gamut_view

    @gamut_view.setter
    def gamut_view(self, value):
        """
        Setter for **self.gamut_view** attribute.

        Parameters
        ----------
        value : ViewBox
            Attribute value.
        """

        raise AttributeError(
            '"{0}" attribute is read only!'.format('gamut_view'))

    @property
    def image_view(self):
        """
        Property for **self.image_view** attribute.

        Returns
        -------
        ViewBox
        """

        return self._image_view

    @image_view.setter
    def image_view(self, value):
        """
        Setter for **self.image_view** attribute.

        Parameters
        ----------
        value : ViewBox
            Attribute value.
        """

        raise AttributeError(
            '"{0}" attribute is read only!'.format('image_view'))

    @property
    def diagram_view(self):
        """
        Property for **self.diagram_view** attribute.

        Returns
        -------
        ViewBox
        """

        return self._diagram_view

    @diagram_view.setter
    def diagram_view(self, value):
        """
        Setter for **self.diagram_view** attribute.

        Parameters
        ----------
        value : ViewBox
            Attribute value.
        """

        raise AttributeError(
            '"{0}" attribute is read only!'.format('diagram_view'))

    @property
    def clamp_blacks(self):
        """
        Property for **self._clamp_blacks** private attribute.

        Returns
        -------
        unicode
            self._clamp_blacks.
        """

        return self._clamp_blacks

    @clamp_blacks.setter
    def clamp_blacks(self, value):
        """
        Setter for **self._clamp_blacks** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert isinstance(value, bool), (
                '"{0}" attribute: "{1}" is not a "bool" instance!'.format(
                    'clamp_blacks', value))

        self._clamp_blacks = value

        image = self._create_image()

        for view in self._views:
            if hasattr(view, 'image'):
                view.image = image

    @property
    def clamp_whites(self):
        """
        Property for **self._clamp_whites** private attribute.

        Returns
        -------
        unicode
            self._clamp_whites.
        """

        return self._clamp_whites

    @clamp_whites.setter
    def clamp_whites(self, value):
        """
        Setter for **self._clamp_whites** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert isinstance(value, bool), (
                '"{0}" attribute: "{1}" is not a "bool" instance!'.format(
                    'clamp_whites', value))

        self._clamp_whites = value

        image = self._create_image()

        for view in self._views:
            if hasattr(view, 'image'):
                view.image = image

    def on_key_press(self, event):
        """
        Reimplements :meth:`vispy.scene.SceneCanvas.on_key_press` method and
        triggers the various actions defined by :class:`ColourAnalysis` class
        and its children views.

        Parameters
        ----------
        event : Object
            Event.
        """

        key = event.key.name.lower()
        modifiers = sorted([modifier.name.lower()
                            for modifier in event.modifiers])
        for action in self._actions.values():
            if (key == action.sequence.key and
                        modifiers == sorted(action.sequence.modifiers)):
                method = '{0}_action'.format(action.name)

                hasattr(self, method) and getattr(self, method)()

                for view in self._views:
                    hasattr(view, method) and getattr(view, method)()

    def _create_layout_presets(self):
        """
        Creates the layout presets from :attr:`ColourAnalysis.settings`
        attribute *layout* key value.

        Notes
        -----
        -   There is no way to change the current layout at the moment.
        """

        layouts = self._settings['layouts']
        for layout in layouts:
            views = {}
            for name, view in layout['views'].items():
                views[name] = ViewPreset(
                    name=view['name'],
                    description=view['description'],
                    view=view['view'],
                    row=view['row'],
                    column=view['column'],
                    row_span=view['row_span'],
                    column_span=view['column_span'])

            self._layout_presets[layout['name']] = LayoutPreset(
                name=layout['name'],
                description=layout['description'],
                views=views)

    def _create_actions(self):
        """
        Creates the actions from :attr:`ColourAnalysis.settings` attribute
        *actions* key value.
        """

        self._actions = {}

        for name, action in self._settings.get('actions', ()).items():
            if action.get('sequence') is not None:
                sequence = Sequence(
                    modifiers=action.get('sequence').get('modifiers', ()),
                    key=action.get('sequence').get('key'))
            else:
                sequence = Sequence(modifiers=(), key=None)

            self._actions[name] = Action(
                name=action.get('name'),
                description=action.get('description'),
                sequence=sequence)

    def _create_views(self):
        """
        Creates the views from :attr:`ColourAnalysis.settings` attribute value.
        """

        background_colour = (
            self._settings['scene_canvas']['views_background_colour'])
        border_colour = self._settings['scene_canvas']['views_border_colour']

        self._console_view = ConsoleView(
            scene_canvas=self,
            text_color=(0.8, 0.8, 0.8),
            font_size=10.0,
            bgcolor=background_colour,
            border_color=border_colour)

        views = self._layout_presets.get(self._layout).views.values()
        views = [view.view for view in views]

        if 'gamut_view' in views:
            self._gamut_view = GamutView(
                scene_canvas=self,
                image=self._image,
                input_colourspace=self._input_colourspace,
                reference_colourspace=self._reference_colourspace,
                correlate_colourspace=self._correlate_colourspace,
                settings=self._settings,
                bgcolor=background_colour,
                border_color=border_colour)

        if 'image_view' in views:
            self._image_view = ImageView(
                scene_canvas=self,
                image=self._image,
                input_colourspace=self._input_colourspace,
                correlate_colourspace=self._correlate_colourspace,
                bgcolor=background_colour,
                border_color=border_colour)

        if 'diagram_view' in views:
            self._diagram_view = DiagramView(
                scene_canvas=self,
                image=self._image,
                input_colourspace=self._input_colourspace,
                correlate_colourspace=self._correlate_colourspace,
                bgcolor=background_colour,
                border_color=border_colour)

        self._views = (self._console_view,
                       self._gamut_view,
                       self._image_view,
                       self._diagram_view)

    def _layout_views(self):
        """
        Layout the views according to :attr:`ColourAnalysis.layout` attribute
        value.
        """

        self._grid = self.central_widget.add_grid()
        layout = self._layout_presets.get(self._layout)

        for view_preset in layout.views.values():
            view = getattr(self, '{0}'.format(view_preset.view))
            if view is None:
                continue

            self._grid.add_widget(
                view,
                row=view_preset.row,
                col=view_preset.column,
                row_span=view_preset.row_span,
                col_span=view_preset.column_span)

    def _create_image(self):
        """
        Creates the image used by the *Diagram View* according to
        :attr:`ColourAnalysis.clamp_blacks` and
        :attr:`ColourAnalysis.clamp_whites` attributes values.

        Returns
        -------
        ndarray
            Image
        """

        image = self._image

        if self._clamp_blacks:
            image = np.clip(image, 0, np.inf)

        if self._clamp_whites:
            image = np.clip(image, -np.inf, 1)

        return image

    def cycle_correlate_colourspace_action(self):
        """
        Defines the slot triggered by the *cycle_correlate_colourspace* action.

        Returns
        -------
        bool
            Definition success.
        """

        self._correlate_colourspace = next(self._RGB_colourspaces_cycle)

        for view in self._views:
            if hasattr(view, 'correlate_colourspace'):
                view.correlate_colourspace = self._correlate_colourspace

        return True

    def cycle_reference_colourspace_action(self):
        """
        Defines the slot triggered by the *cycle_reference_colourspace* action.

        Returns
        -------
        bool
            Definition success.
        """

        self._reference_colourspace = next(
            self._reference_colourspaces_cycle)

        for view in self._views:
            if hasattr(view, 'reference_colourspace'):
                view.reference_colourspace = self._reference_colourspace

        return True

    def toggle_blacks_clamp_action(self):
        """
        Defines the slot triggered by the *toggle_blacks_clamp* action.

        Returns
        -------
        bool
            Definition success.
        """

        self.clamp_blacks = not self.clamp_blacks

        return True

    def toggle_whites_clamp_action(self):
        """
        Defines the slot triggered by the *toggle_whites_clamp* action.

        Returns
        -------
        bool
            Definition success.
        """

        self.clamp_whites = not self.clamp_whites

        return True
