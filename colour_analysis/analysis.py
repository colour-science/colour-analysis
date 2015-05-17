# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import json
import numpy as np
import os
from collections import OrderedDict, deque, namedtuple
from itertools import cycle

from vispy.scene import SceneCanvas

from colour import RGB_COLOURSPACES, message_box, read_image

from colour_analysis.common import REFERENCE_COLOURSPACES
from colour_analysis.constants import DEFAULT_IMAGE, SETTINGS_FILE

from colour_analysis.gamut_view import GamutView
from colour_analysis.image_view import ImageView


Sequence = namedtuple('Sequence', ('modifiers', 'key'))

Action = namedtuple('Action', ('name', 'description', 'sequence'))


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
                             title="Colour Analysis - {0}".format(
                                 image_path),
                             bgcolor=settings.get('canvas').get(
                                 'background_colour'))

        self.__image_path = None
        self.image_path = image_path
        self.__image = None
        self.image = np.random.random((256, 256, 3))
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

        self.__actions = {}

        self.__grid = None
        self.__gamut_view = None
        self.__image_view = None
        self.__diagram_view = None
        self.__views = None

        self.__RGB_colourspaces_cycle = cycle(
            [c for c in sorted(RGB_COLOURSPACES)
             if c not in ('aces', 'adobe1998', 'prophoto')])

        reference_colourspaces_deque = deque(REFERENCE_COLOURSPACES)
        reference_colourspaces_deque.rotate(-REFERENCE_COLOURSPACES.index(
            self.__reference_colourspace) - 1)
        self.__reference_colourspaces_cycle = cycle(
            reference_colourspaces_deque)

        self.initialise_actions()
        self.initialise_image()
        self.initialise_views()

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

    def on_key_press(self, event):
        key = event.key.name
        modifiers = sorted([modifier.name for modifier in event.modifiers])
        for action in self.__actions.values():
            if (key == action.sequence.key and
                        modifiers == sorted(action.sequence.modifiers)):
                method = '{0}_action'.format(action.name)

                hasattr(self, method) and getattr(self, method)()

                for view in self.__views:
                    hasattr(view, method) and getattr(view, method)()

    def initialise_image(self):
        image = read_image(self.__image_path)
        if not self.__input_linear:
            colourspace = RGB_COLOURSPACES[self.__input_oecf]
            image = colourspace.inverse_transfer_function(image)

        self.__image = image

        return True

    def initialise_actions(self):
        self.__actions = {}

        for name, action in self.__settings.get('actions', ()).items():
            if action.get('sequence') is not None:
                sequence = Sequence(
                    modifiers=action.get('sequence').get('modifiers', ()),
                    key=action.get('sequence').get('key'))
            else:
                sequence = Sequence(modifiers=(), key=None)

            self.__actions[name] = Action(
                name=action.get('name'),
                description=action.get('description'),
                sequence=sequence)

    def initialise_views(self):
        self.__grid = self.central_widget.add_grid()

        border_colour = self.__settings.get('canvas').get('border_colour')

        self.__gamut_view = GamutView(
            image=self.__image,
            input_colourspace=self.__input_colourspace,
            reference_colourspace=self.__reference_colourspace,
            correlate_colourspace=self.__correlate_colourspace,
            settings=self.__settings,
            border_color=border_colour)
        self.__grid.add_widget(self.__gamut_view, row=0, col=0, row_span=2)

        self.__image_view = ImageView(
            image=self.__image,
            oecf=self.__input_oecf,
            border_color=border_colour)
        self.__grid.add_widget(self.__image_view, row=0, col=1)

        self.__diagram_view = self.__grid.add_view(row=1, col=1)
        self.__diagram_view.border_color = border_colour

        self.__views = (self.__gamut_view,
                        self.__image_view,
                        self.__diagram_view)

        return True

    def print_actions_action(self):
        actions = []
        for _name, action in sorted(self.__actions.items()):
            if action.sequence.modifiers:
                sequence = '{0} + {1}'.format(
                    ' + '.join(action.sequence.modifiers),
                    action.sequence.key)
            else:
                sequence = '{0}'.format(action.sequence.key)
            actions.append('- {0}: {1}'.format(action.description, sequence))

        message_box('Actions & Shortcuts\n\n{0}'.format(
            '\n'.join(actions)))

        return True

    def print_analysis_state_action(self):

        state = []
        state.append('- Input image: {0}'.format(
            self.__image_path))
        state.append('- Input RGB colourspace: {0}'.format(
            self.__input_colourspace))
        state.append('- Input OECF: {0}'.format(
            self.__input_oecf))
        state.append('- Input linearity: {0}'.format(
            self.__input_linear))
        state.append('- Reference colourspace: {0}'.format(
            self.__reference_colourspace))
        state.append('- Correlate RGB colourspace: {0}'.format(
            self.__correlate_colourspace))
        message_box('Analysis State\n\n{0}'.format(
            '\n'.join(state)))

        return True

    def cycle_correlate_colourspace_action(self):
        self.__correlate_colourspace = next(self.__RGB_colourspaces_cycle)
        self.__gamut_view.correlate_colourspace = self.__correlate_colourspace

        return True

    def cycle_reference_colourspace_action(self):

        self.__reference_colourspace = next(
            self.__reference_colourspaces_cycle)

        self.__gamut_view.reference_colourspace = self.__reference_colourspace

        return True