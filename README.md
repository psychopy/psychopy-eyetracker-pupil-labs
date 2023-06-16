# psychopy-eyetracker-pupil-labs

Extension for PsychoPy which adds support for [Pupil Labs](https://pupil-labs.com/) 
eyetrackers (via ioHub)

## Supported Devices

Installing this package alongside PsychoPy will enable support for the following 
devices:

* Supported Pupil Labs eye trackers
    
## Installing

Install this package with the following shell command:: 

    pip install psychopy-eyetracker-pupil-labs

You may also use PsychoPy's builtin plugin/package manager to install this 
package.

## Usage

Once the package is installed, PsychoPy will automatically load it when started 
and the `psychopy.iohub.devices.eyetracker.hw.pupil_labs` namespace will contain 
the loaded objects.