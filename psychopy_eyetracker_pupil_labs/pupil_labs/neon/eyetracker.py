# -*- coding: utf-8 -*-
# Part of the PsychoPy library
# Copyright (C) 2012-2020 iSolver Software Solutions (C) 2021 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).
import logging
from typing import Optional, Dict, Tuple, Union

from psychopy.iohub.constants import EyeTrackerConstants
from psychopy.iohub.devices import Computer, Device
from psychopy.iohub.devices.eyetracker import EyeTrackerDevice
from psychopy.iohub.errors import printExceptionDetailsToStdErr
from psychopy.iohub.constants import EventConstants

from pupil_labs.realtime_api.simple import Device as CompanionDevice
from pupil_labs.real_time_screen_gaze.gaze_mapper import GazeMapper


class EyeTracker(EyeTrackerDevice):
    """
    Implementation of the :py:class:`Common Eye Tracker Interface <.EyeTrackerDevice>`
    for the Pupil Core headset.

    Uses ioHub's polling method to process data from `Pupil Capture's Network API
    <https://docs.pupil-labs.com/developer/core/network-api/>`_.

    To synchronize time between Pupil Capture and PsychoPy, the integration estimates
    the offset between their clocks and applies it to the incoming data. This step
    effectively transforms time between the two softwares while taking the transmission
    delay into account. For details, see this `real-time time-sync tutorial
    <https://github.com/pupil-labs/pupil-helpers/blob/master/python/simple_realtime_time_sync.py>`_.

    .. note::

        Only **one** instance of EyeTracker can be created within an experiment.
        Attempting to create > 1 instance will raise an exception.

    """

    # EyeTrackerDevice Interface

    # #: The multiplier needed to convert a device's native time base to sec.msec-usec times.
    # DEVICE_TIMEBASE_TO_SEC = 1.0

    # Used by pyEyeTrackerDevice implementations to store relationships between an eye
    # trackers command names supported for EyeTrackerDevice sendCommand method and
    # a private python function to call for that command. This allows an implementation
    # of the interface to expose functions that are not in the core EyeTrackerDevice spec
    # without have to use the EXT extension class.
    _COMMAND_TO_FUNCTION = {}

    EVENT_CLASS_NAMES = [
        "BinocularEyeSampleEvent",
    ]

    def __init__(self, *args, **kwargs) -> None:
        EyeTrackerDevice.__init__(self, *args, **kwargs)

        self._device = None
        self._time_offset_estimate = None

        self._latest_sample = None
        self._latest_gaze_position = None
        self._actively_recording = False

        self._screen_surface = None
        self._window_size = None

        self._gaze_mapper = None

        self.setConnectionState(True)

    def trackerTime(self) -> float:
        """Returns the current time reported by the eye tracker device.

        Implementation measures the current time in PsychoPy time and applies the
        estimated clock offset to transform the measurement into tracker time.

        :return: The eye tracker hardware's reported current time.

        """
        return self._psychopyTimeInTrackerTime(Computer.getTime())

    def trackerSec(self) -> float:
        """
        Returns :py:func:`.EyeTracker.trackerTime`

        :return: The eye tracker hardware's reported current time in sec.msec-usec format.
        """
        return self.trackerTime()

    def setConnectionState(self, enable: bool) -> None:
        """setConnectionState either connects (``setConnectionState(True)``) or
        disables (``setConnectionState(False)``) active communication between the
        ioHub and Pupil Capture.

        .. note::
            A connection to the Eye Tracker is automatically established
            when the ioHub Process is initialized (based on the device settings
            in the iohub_config.yaml), so there is no need to
            explicitly call this method in the experiment script.

        .. note::
            Connecting an Eye Tracker to the ioHub does **not** necessarily collect and
            send eye sample data to the ioHub Process. To start actual data collection,
            use the Eye Tracker method ``setRecordingState(bool)`` or the ioHub Device
            method (device type independent) ``enableEventRecording(bool)``.

        Args:
            enable (bool): True = enable the connection, False = disable the connection.

        :return:
            bool: indicates the current connection state to the eye tracking hardware.
        """
        if enable and self._device is None:
            self._device = CompanionDevice(
                self._runtime_settings["companion_address"],
                int(self._runtime_settings["companion_port"]),
            )

            calibration = self._device.get_calibration()
            self._gaze_mapper = GazeMapper(calibration)

            self._time_offset_estimate = self._device.estimate_time_offset()
            self._device.receive_matched_scene_video_frame_and_gaze()

        elif not enable and self._device is not None:
            self._device.close()
            self._device = None

    def isConnected(self) -> bool:
        """isConnected returns whether the ioHub EyeTracker Device is connected
        to Pupil Capture or not. A Pupil Core headset must be connected and working
        properly for any of the Common Eye Tracker Interface functionality to work.

        Args:
            None

        :return:
            bool:  True = the eye tracking hardware is connected. False otherwise.

        """
        return self._device is not None

    def runSetupProcedure(self, calibration_args: Optional[Dict] = None) -> int:
        """
        The runSetupProcedure method starts the Pupil Capture calibration choreography.

        .. note::
            This is a blocking call for the PsychoPy Process and will not return to the
            experiment script until the calibration procedure was either successful,
            aborted, or failed.

        :param calibration_args: This argument will be ignored and has only been added
            for the purpose of compatibility with the Common Eye Tracker Interface

        :return:
            - :py:attr:`.EyeTrackerConstants.EYETRACKER_OK`
                if the calibration was succesful
            - :py:attr:`.EyeTrackerConstants.EYETRACKER_SETUP_ABORTED`
                if the choreography was aborted by the user
            - :py:attr:`.EyeTrackerConstants.EYETRACKER_CALIBRATION_ERROR`
                if the calibration failed, check logs for details
            - :py:attr:`.EyeTrackerConstants.EYETRACKER_ERROR`
                if any other error occured, check logs for details
        """
        return EyeTrackerConstants.EYETRACKER_OK

    def setRecordingState(self, should_be_recording: bool) -> bool:
        """The setRecordingState method is used to start or stop the recording
        and transmission of eye data from the eye tracking device to the ioHub
        Process.

        If the ``pupil_capture_recording.enabled`` runtime setting is set to ``True``,
        a corresponding raw recording within Pupil Capture will be started or stopped.

        ``should_be_recording`` will also be passed to
        :py:func:`.EyeTrackerDevice.enableEventReporting`.

        Args:
            recording (bool): if True, the eye tracker will start recordng data.;
                false = stop recording data.

        :return:
            bool: the current recording state of the eye tracking device

        """
        if not self.isConnected():
            return False

        if should_be_recording:
            self._device.recording_start()
        else:
            try:
                self._device.recording_stop_and_save()
            except Exception as exc:
                logging.error(f"Failed to stop recording: {exc}")
                printExceptionDetailsToStdErr()

        self._actively_recording = should_be_recording

        is_recording_enabled = self.isRecordingEnabled()

        if not is_recording_enabled:
            self._latest_sample = None
            self._latest_gaze_position = None

        return EyeTrackerDevice.enableEventReporting(self, self._actively_recording)

    def isRecordingEnabled(self) -> bool:
        """The isRecordingEnabled method indicates if the eye tracker device is
        currently recording data.

        :return: ``True`` == the device is recording data; ``False`` == Recording is not
            occurring

        """
        if not self.isConnected():
            return False
        return self._actively_recording

    def getLastSample(self) -> Union[
        None,
        "psychopy.iohub.devices.eyetracker.BinocularEyeSampleEvent",
    ]:
        """The getLastSample method returns the most recent eye sample received
        from the Eye Tracker. The Eye Tracker must be in a recording state for
        a sample event to be returned, otherwise None is returned.

        :return:

            - BinocularEyeSample:
                Gaze mapping result from two combined pupil detections
            - None:
                If the eye tracker is not currently recording data.

        """
        return self._latest_sample

    def getLastGazePosition(self) -> Optional[Tuple[float, float]]:
        """The getLastGazePosition method returns the most recent eye gaze
        position received from the Eye Tracker. This is the position on the
        calibrated 2D surface that the eye tracker is reporting as the current
        eye position. The units are in the units in use by the ioHub Display
        device.

        If binocular recording is being performed, the average position of both
        eyes is returned.

        If no samples have been received from the eye tracker, or the
        eye tracker is not currently recording data, None is returned.

        :return:

            - None:
                If the eye tracker is not currently recording data or no eye samples
                have been received.

            - tuple:
                Latest (gaze_x,gaze_y) position of the eye(s)
        """
        return self._latest_gaze_position

    def _poll(self):
        if not self.isConnected():
            return

        if self._screen_surface is None:
            return

        frame_and_gaze = self._device.receive_matched_scene_video_frame_and_gaze(timeout_seconds=0)

        if frame_and_gaze is None:
            return

        logged_time = Computer.getTime()

        frame, gaze = frame_and_gaze
        surface_map = self._gaze_mapper.process_frame(frame, gaze)
        for surface_gaze in surface_map.mapped_gaze[self._screen_surface.uid]:

            gaze_in_pix = [
                surface_gaze.x * self._window_size[0],
                surface_gaze.y * self._window_size[1],
            ]

            gaze_in_display_units = self._eyeTrackerToDisplayCoords(gaze_in_pix)

            self._add_gaze_sample(gaze_in_display_units, gaze, logged_time)

    def _add_gaze_sample(self, surface_gaze, gaze_datum, logged_time):
        native_time = gaze_datum.timestamp_unix_seconds
        iohub_time = self._trackerTimeInPsychopyTime(native_time)

        metadata = {
            "experiment_id": 0,  # experiment_id, iohub fills in automatically
            "session_id": 0,  # session_id, iohub fills in automatically
            "device_id": 0,  # device_id, keep at 0
            "event_id": Device._getNextEventID(),  # iohub event unique ID
            "device_time": native_time,
            "logged_time": logged_time,
            "time": iohub_time,
            "confidence_interval": -1.0,
            "delay": (logged_time - iohub_time),
            "filter_id": False,
        }

        sample = [  # BinocularEyeSampleEvent
            metadata["experiment_id"],
            metadata["session_id"],
            metadata["device_id"],
            metadata["event_id"],
            EventConstants.BINOCULAR_EYE_SAMPLE,  # type
            metadata["device_time"],
            metadata["logged_time"],
            metadata["time"],
            metadata["confidence_interval"],
            metadata["delay"],
            metadata["filter_id"],

            surface_gaze[0],                # left_gaze_x
            surface_gaze[1],                # left_gaze_y
            EyeTrackerConstants.UNDEFINED,  # left_gaze_z
            EyeTrackerConstants.UNDEFINED,  # left_eye_cam_x
            EyeTrackerConstants.UNDEFINED,  # left_eye_cam_y
            EyeTrackerConstants.UNDEFINED,  # left_eye_cam_z
            EyeTrackerConstants.UNDEFINED,  # left_angle_x
            EyeTrackerConstants.UNDEFINED,  # left_angle_y
            gaze_datum.x,                   # left_raw_x
            gaze_datum.y,                   # left_raw_y
            EyeTrackerConstants.UNDEFINED,  # left_pupil_measure1
            EyeTrackerConstants.UNDEFINED,  # pupil_measure1_type  # left_pupil_measure1_type
            EyeTrackerConstants.UNDEFINED,  # left_pupil_measure2
            EyeTrackerConstants.UNDEFINED,  # pupil_measure2_type  # left_pupil_measure2_type
            EyeTrackerConstants.UNDEFINED,  # left_ppd_x
            EyeTrackerConstants.UNDEFINED,  # left_ppd_y
            EyeTrackerConstants.UNDEFINED,  # left_velocity_x
            EyeTrackerConstants.UNDEFINED,  # left_velocity_y
            EyeTrackerConstants.UNDEFINED,  # left_velocity_xy

            surface_gaze[0],                # right_gaze_x
            surface_gaze[1],                # right_gaze_y
            EyeTrackerConstants.UNDEFINED,  # gaze_z,  # right_gaze_z
            EyeTrackerConstants.UNDEFINED,  # right_eye_cam_x
            EyeTrackerConstants.UNDEFINED,  # right_eye_cam_y
            EyeTrackerConstants.UNDEFINED,  # right_eye_cam_z
            EyeTrackerConstants.UNDEFINED,  # right_angle_x
            EyeTrackerConstants.UNDEFINED,  # right_angle_y
            gaze_datum.x,                   # right_raw_x
            gaze_datum.y,                   # right_raw_y
            EyeTrackerConstants.UNDEFINED,  # right_pupil_measure1
            EyeTrackerConstants.UNDEFINED,  # pupil_measure1_type  # right_pupil_measure1_type
            EyeTrackerConstants.UNDEFINED,  # right_pupil_measure2
            EyeTrackerConstants.UNDEFINED,  # pupil_measure2_type  # right_pupil_measure2_type
            EyeTrackerConstants.UNDEFINED,  # right_ppd_x
            EyeTrackerConstants.UNDEFINED,  # right_ppd_y
            EyeTrackerConstants.UNDEFINED,  # right_velocity_x
            EyeTrackerConstants.UNDEFINED,  # right_velocity_y
            EyeTrackerConstants.UNDEFINED,  # right_velocity_xy
            0,
        ]

        self._addNativeEventToBuffer(sample)

        self._latest_sample = sample
        self._latest_gaze_position = surface_gaze

    def register_surface(self, tag_verts, window_size):
        corrected_verts = {}
        for tag_id_str, verts in tag_verts.items():
            corrected_verts[int(tag_id_str)] = [
                (vert[0] + window_size[0] / 2, vert[1] + window_size[1] / 2) for vert in verts
            ]

        self._gaze_mapper.clear_surfaces()
        self._screen_surface = self._gaze_mapper.add_surface(
            corrected_verts,
            window_size
        )

        self._window_size = window_size

    def _psychopyTimeInTrackerTime(self, psychopy_time):
        return psychopy_time + self._time_offset_estimate.time_offset_ms.mean / 1000

    def _trackerTimeInPsychopyTime(self, tracker_time):
        return tracker_time - self._time_offset_estimate.time_offset_ms.mean / 1000

    def _close(self):
        """Do any final cleanup of the eye tracker before the object is
        destroyed."""
        self.setConnectionState(False)
        self.__class__._INSTANCE = None
        super()._close()
