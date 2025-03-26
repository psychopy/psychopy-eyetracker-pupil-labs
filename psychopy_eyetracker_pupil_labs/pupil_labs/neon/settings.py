from psychopy.localization import _translate
from psychopy.experiment import Param
from psychopy.experiment.components.settings.eyetracking import EyetrackerBackend


class PupilLabsNeonEyetrackerBackend(EyetrackerBackend):
    """Experiment settings for Pupil Labs Neon eyetrackers.
    """
    label = 'Pupil Labs Neon (iohub)'
    key = 'eyetracker.hw.pupil_labs.neon.EyeTracker'

    needsFullscreen = False
    needsCalibration = False

    @classmethod
    def getParams(cls):
        # define order
        order = [
            # runtime settings
            "plCompanionAddress",
            "plCompanionPort"
        ]

        # runtime settings
        params = {}
        params['plCompanionAddress'] = Param(
            "neon.local",   # default value
            valType='str', 
            inputType="single",
            hint=_translate("Address to connect to."),
            label=_translate("Companion Address"), 
            categ="Eyetracking"
        )
        params['plCompanionPort'] = Param(
            "8080",  # default value
            valType='str', 
            inputType="single",
            hint=_translate("Port number to connect to."),
            label=_translate("Companion Port"), 
            categ="Eyetracking"
        )
        
        return params, order

    @classmethod
    def writeDeviceCode(cls, inits, buff):
        code = (
            "ioConfig[%(eyetracker)s] = {\n"
            "    'name': 'tracker',\n"
            "    'runtime_settings': {\n"
            "       'companion_address': %(plRemoteAddress)s,\n"
            "       'companion_port': %(plRemotePort)s,\n"
            "    },\n"
            "}\n"
        )
        buff.writeIndentedLines(code % inits)
