from psychopy.localization import _translate
from psychopy.experiment import Param
from psychopy.experiment.components.settings.eyetracking import EyetrackerBackend


class PupilLabsCoreEyetrackerBackend(EyetrackerBackend):
    """Experiment settings for Pupil Labs Core eyetrackers.
    """
    label = 'Pupil Labs Core (iohub)'
    key = 'eyetracker.hw.pupil_labs.pupil_core.EyeTracker'

    needsFullscreen = False
    needsCalibration = False

    @classmethod
    def getParams(cls):
        # define order
        order = [
            # runtime settings
            "plRemoteAddress",
            "plRemotePort",
            "plRemoteTimeout",
            "plPupillometryOnly",
            "plSurfaceName",
            "plGazeConfidenceThreshold",
            "plEnableCaptureRecording",
            "plCaptureRecordingPath",
        ]

        # network settings
        params = {}
        params['plRemoteAddress'] = Param(
            "127.0.0.1",   # default value
            valType='str', 
            inputType="single",
            hint=_translate("IP Address to connect to."),
            label=_translate("Pupil Remote Address"), 
            categ="Eyetracking"
        )
        params['plRemotePort'] = Param(
            "50020",  # default value
            valType='str', 
            inputType="single",
            hint=_translate("Port number to connect to."),
            label=_translate("Pupil Remote Port"), 
            categ="Eyetracking"
        )
        params['plRemoteTimeout'] = Param(
            "1000",  # default value
            valType='str', 
            inputType="single",
            hint=_translate("Timeout in milliseconds."),
            label=_translate("Pupil Remote Timeout (ms)"), 
            categ="Eyetracking"
        )

        # runtime settings
        params['plPupillometryOnly'] = Param(
            False, 
            valType='str', 
            inputType="bool",
            hint=_translate("Subscribe to pupil data only, does not require calibration or surface setup."),
            label=_translate("Pupillometry only?"), 
            categ="Eyetracking"
        )
        params['plSurfaceName'] = Param(
            "psychopy_iohub_surface", 
            valType='str', 
            inputType="single",
            hint=_translate("Name of the surface to track."),
            label=_translate("Surface name"), 
            categ="Eyetracking"
        )
        params['plGazeConfidenceThreshold'] = Param(
            "0.6", 
            valType='str', 
            inputType="single",
            hint=_translate("Gaze confidence threshold."),
            label=_translate("Gaze confidence threshold"), 
            categ="Eyetracking"
        )
        params['plEnableCaptureRecording'] = Param(
            False, 
            valType='str', 
            inputType="bool",
            hint=_translate("Enable capture recording."),
            label=_translate("Pupil Capture Recording Enabled?"), 
            categ="Eyetracking"
        )
        params['plCaptureRecordingPath'] = Param(
            "", 
            valType='str', 
            inputType="single",
            hint=_translate("Path to save capture recordings."),
            label=_translate("Pupil Capture Recording Location"), 
            categ="Eyetracking"
        )

        return params, order

    @classmethod
    def writeDeviceCode(cls, inits, buff):
        code = (
            "ioConfig[%(eyetracker)s] = {\n"
            "    'name': 'tracker',\n"
            "    'runtime_settings': {\n"
            "        'pupil_remote': {\n"
            "           'ip_address': %(plRemoteAddress)s,\n"
            "           'port': %(plRemotePort)s,\n"
            "           'timeout_ms': %(plRemoteTimeout)s,\n"
            "        },\n"
            "        'pupil_capture_recording': {\n"
            "           'enabled': %(plEnableCaptureRecording)s,\n"
            "           'location': %(plCaptureRecordingPath)s,\n"
            "        },\n"
            "        'pupillometry_only': %(plPupillometryOnly)s,\n"
            "        'surface_name': %(plSurfaceName)s,\n"
            "        'confidence_threshold': %(plGazeConfidenceThreshold)s,\n"
            "    },\n"
            "}\n"
        )
        buff.writeIndentedLines(code % inits)
