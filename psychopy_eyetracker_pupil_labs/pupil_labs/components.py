from pathlib import Path

from psychopy.experiment.components import BaseVisualComponent, Param, getInitVals
from psychopy.localization import _translate


class AprilTagComponent(BaseVisualComponent):
    targets = ['PsychoPy']
    categories = ['Eyetracking']
    iconFile = Path(__file__).parent.parent / 'apriltag.png'
    tooltip = _translate('AprilTag: Markers to identify a screen surface')

    _instances = []
    _routine_start_written = False

    def __init__(self, exp, parentName, marker_id=0, anchor="center", size=(0.2, 0.2), startType='time (s)', startVal=0.0, *args, **kwargs):
        super().__init__(exp, parentName, size=size, startType=startType, startVal=startVal, *args, **kwargs)

        self.type = 'Image'
        self.url = "https://april.eecs.umich.edu/software/apriltag.html"
        self.exp.requirePsychopyLibs(['visual'])
        self.exp.requireImport('AprilTagStim', 'psychopy_eyetracker_pupil_labs.pupil_labs.stimuli')
        self.exp.requireImport('convertToPix', 'psychopy.tools.monitorunittools')

        self.order += ['marker_id']

        self.params['marker_id'] = Param(marker_id,
            valType='int', inputType="spin", categ='Basic',
            updates='constant', allowedVals=[0, 512],
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
            label=_translate("Anchor")
        )

        del self.params['color']
        del self.params['colorSpace']
        del self.params['fillColor']
        del self.params['borderColor']
        del self.params['opacity']
        del self.params['ori']

        self.marker_id = marker_id
        AprilTagComponent._instances.append(self)

    def writeInitCode(self, buff):
        AprilTagComponent._routine_start_written = False

        # replace variable params with defaults
        inits = getInitVals(self.params, 'PsychoPy')
        code = ("{inits[name]} = AprilTagStim(\n"
                "    win=win,\n"
                "    name='{inits[name]}', units={inits[units]},\n"
                "    contrast={inits[contrast]},\n"
                "    marker_id=int({inits[marker_id]}), anchor={inits[anchor]},\n"
                "    pos={inits[pos]}, size={inits[size]}"
                .format(inits=inits))

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
            code += "        str({inits[name]}.marker_id): {inits[name]}.marker_verts,\n".format(inits=inits)

        code += "    }\n"
        code += "    win_size_pix = convertToPix(np.array([2, 2]), [0, 0], 'norm', win)\n"
        code += "    eyetracker.register_surface(tag_verts, win_size_pix)\n"
        buff.writeIndentedLines(code)

        AprilTagComponent._routine_start_written = True


class AprilTagFrameComponent(BaseVisualComponent):
    targets = ['PsychoPy']
    categories = ['Eyetracking']
    iconFile = Path(__file__).parent.parent / 'apriltag_frame.png'
    tooltip = _translate('AprilTag: Markers to identify a screen surface')

    def __init__(self, exp, parentName, h_count=3, v_count=3, marker_ids='', marker_size=0.125, marker_units="from exp settings", anchor="center", size=[2, 2], units="norm", startType='time (s)', startVal=0.0, *args, **kwargs):
        super().__init__(exp, parentName, size=size, units=units, startType=startType, startVal=startVal, *args, **kwargs)

        self.type = 'Image'
        self.url = "https://april.eecs.umich.edu/software/apriltag.html"
        self.exp.requirePsychopyLibs(['visual'])
        self.exp.requireImport('AprilTagFrameStim', 'psychopy_eyetracker_pupil_labs.pupil_labs.stimuli')
        self.exp.requireImport('convertToPix', 'psychopy.tools.monitorunittools')

        self.params['h_count'] = Param(h_count,
            valType='int', inputType="spin", categ='Basic',
            updates='constant', allowedVals=[0, 64],
            allowedUpdates=['constant'],
            hint=_translate("The number of AprilTag markers to display along the horizontal edges of the display"),
            label=_translate("Horizontal Count"))

        self.params['v_count'] = Param(v_count,
            valType='int', inputType="spin", categ='Basic',
            updates='constant', allowedVals=[0, 64],
            allowedUpdates=['constant'],
            hint=_translate("The number of AprilTag markers to display along the vertical edges of the display"),
            label=_translate("Vertical Count"))

        self.params['marker_ids'] = Param(marker_ids,
            valType='str', categ='Basic',
            updates='constant',
            allowedUpdates=['constant'],
            hint=_translate("The IDs of the AprilTag marker to display"),
            label=_translate("Marker IDs"))

        self.params['marker_size'] = Param(marker_size,
            valType='int', inputType="single", categ='Layout',
            updates='constant', allowedTypes=[],
            allowedUpdates=['constant'],
            hint=_translate("The size of each AprilTag marker"),
            label=_translate("Marker size [w,h]"))

        self.params['marker_units'] = Param(marker_units,
            valType='str', inputType="choice", categ='Layout',
            allowedVals=['from exp settings', 'deg', 'cm', 'pix', 'norm',
                         'height', 'degFlatPos', 'degFlat'],
            hint=_translate("Marker size spatial units"),
            label=_translate("Marker size spatial units"))

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

        del self.params['color']
        del self.params['colorSpace']
        del self.params['fillColor']
        del self.params['borderColor']
        del self.params['opacity']
        del self.params['ori']

    def writeInitCode(self, buff):
        inits = getInitVals(self.params, 'PsychoPy')
        if inits['marker_ids'] in ('', 'None'):
            marker_count = 2 * (int(inits['h_count'].val) + int(inits['v_count'].val)) - 4
            marker_ids = list(range(marker_count))
        else:
            marker_ids = [v.strip() for v in inits['marker_ids'].val.split(',')]

        if inits['marker_units'].val == 'from exp settings':
            marker_units = self.exp.settings.params['Units']
        else:
            marker_units = inits['marker_units']

        code = (f"{inits['name']} = AprilTagFrameStim(\n"
                f"    win=win,\n"
                f"    name='{inits['name']}', units={inits['units']},\n"
                f"    contrast={inits['contrast']},\n"
                f"    h_count={inits['h_count']}, v_count={inits['v_count']},\n"
                f"    marker_ids={marker_ids}, anchor={inits['anchor']},\n"
                f"    marker_size={inits['marker_size']}, marker_units={marker_units},\n"
                f"    pos={inits['pos']}, size={inits['size']})")

        buff.writeIndentedLines(code)

    def writeRoutineStartCode(self, buff):
        """Write the code that will be called at the beginning of
        a routine (e.g. to update stimulus parameters)
        """
        inits = getInitVals(self.params, 'PsychoPy')
        code = (f"if eyetracker is not None and hasattr(eyetracker, 'register_surface'):\n"
                f"    win_size_pix = convertToPix(np.array([2, 2]), [0, 0], 'norm', win)\n"
                f"    eyetracker.register_surface({inits['name']}.marker_verts, win_size_pix)\n")

        buff.writeIndentedLines(code)
