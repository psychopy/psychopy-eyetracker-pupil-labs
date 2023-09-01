# -*- coding: utf-8 -*-
# Part of the PsychoPy library
# Copyright (C) 2012-2020 iSolver Software Solutions (C) 2021 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

from pathlib import Path

from psychopy.visual import ImageStim
from psychopy.experiment.components import BaseVisualComponent, Param, getInitVals
from psychopy.localization import _translate

import numpy as np

from pupil_labs.realtime_screen_gaze import marker_generator


class AprilTagStim(ImageStim):
    def __init__(self, marker_id=0, *args, **kwargs):
        self.marker_id = marker_id

        marker_data = marker_generator.generate_marker(marker_id, flip_x=True).astype(float)
        marker_data[marker_data == 0] = -1
        marker_data[marker_data > 0] = 1

        marker_data = np.pad(marker_data, pad_width=1, mode="constant", constant_values=1)

        super().__init__(image=marker_data, *args, **kwargs)


    def get_marker_verts(self):
        vertices_in_pixels =  self._vertices.pix
        padding = self.size[0]/10

        top_left_pos = vertices_in_pixels[2]

        top_left = (
            top_left_pos[0] + padding,
            top_left_pos[1] - padding
        )
        bottom_right = (
            top_left_pos[0] + self.size[0] - padding,
            top_left_pos[1] - self.size[1] + padding
        )

        return (
            top_left,
            (bottom_right[0], top_left[1]),
            bottom_right,
            (top_left[0], bottom_right[1]),
        )


class AprilTagComponent(BaseVisualComponent):
    targets = ['PsychoPy']
    categories = ['Eyetracking']
    iconFile = Path(__file__).parent / 'apriltag.png'
    tooltip = _translate('AprilTag: Markers to identify a screen surface')

    _instances = []
    _routine_start_written = False

    def __init__(self, exp, parentName, marker_id=0, anchor="center", *args, **kwargs):
        super(AprilTagComponent, self).__init__(exp, parentName, *args, **kwargs)

        self.type = 'Image'
        self.url = "https://april.eecs.umich.edu/software/apriltag.html"
        self.exp.requirePsychopyLibs(['visual'])
        self.exp.requireImport('AprilTagStim', 'psychopy_eyetracker_pupil_labs')

        self.order += ['marker_id']

        self.params['marker_id'] = Param(marker_id,
            valType='int', inputType="spin", categ='Basic',
            updates='constant', allowedVals=[0,512],
            allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            hint=_translate("The ID of the AprilTag marker to display"),
            label=_translate("Marker ID")
        )

        self.params['anchor'] = Param(
            anchor, valType='str', inputType="choice", categ='Layout',
            allowedVals=['center',
                        'top-center',
                        'bottom-center',
                        'center-left',
                        'center-right',
                        'top-left',
                        'top-right',
                        'bottom-left',
                        'bottom-right',
                        ],
            updates='constant',
            hint=_translate("Which point on the stimulus should be anchored to its exact position?"),
            label=_translate("Anchor"))

        self.marker_id = marker_id
        AprilTagComponent._instances.append(self)


    def writeInitCode(self, buff):
        AprilTagComponent._routine_start_written = False

        # do we need units code?
        if self.params['units'].val == 'from exp settings':
            unitsStr = ""
        else:
            unitsStr = "units=%(units)s, " % self.params

        # replace variable params with defaults
        inits = getInitVals(self.params, 'PsychoPy')
        code = ("{inits[name]} = AprilTagStim(\n"
                "    win=win,\n"
                "    name='{inits[name]}', {units}\n"
                "    marker_id=int({inits[marker_id]}), anchor={inits[anchor]},\n"
                "    pos={inits[pos]}, size={inits[size]}"
                .format(inits=inits, units=unitsStr))

        depth = -self.getPosInRoutine()
        code += ", depth=%.1f)\n" % depth

        buff.writeIndentedLines(code)

    def writeRoutineStartCode(self, buff):
        """Write the code that will be called at the beginning of
        a routine (e.g. to update stimulus parameters)
        """
        if AprilTagComponent._routine_start_written:
            return

        code = ("if eyetracker is not None and hasattr(eyetracker, 'register_surface'):\n"
                "    tag_verts = {\n")

        routine = self.exp.routines[self.parentName]
        tag_comps = [comp for comp in routine if not comp == routine.settings]
        tag_comps = filter(lambda comp: isinstance(comp, AprilTagComponent), tag_comps)

        for component in tag_comps:
            inits = getInitVals(component.params, 'PsychoPy')
            code += "        str({inits[name]}.marker_id): {inits[name]}.get_marker_verts(),\n".format(inits=inits)

        code += "    }\n"
        code += "    eyetracker.register_surface(tag_verts, win.size)"
        buff.writeIndentedLines(code)

        AprilTagComponent._routine_start_written = True
