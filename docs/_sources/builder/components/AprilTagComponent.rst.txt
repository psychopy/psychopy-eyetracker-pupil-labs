-------------------------------
AprilTagComponent
-------------------------------


Categories:
    Eyetracking
Works in:
    PsychoPy

Parameters
-------------------------------

None
===============================

Name
    Name of this Component (alphanumeric or _, no spaces)

Disable Component
    Disable this Component

Basic
===============================

Start type
    How do you want to define your start point?
    
    Options:
    - time (s)
    - frame N
    - condition

Stop type
    How do you want to define your end point?
    
    Options:
    - duration (s)
    - duration (frames)
    - time (s)
    - frame N
    - condition

Start
    When does the Component start?

Stop
    When does the Component end? (blank is endless)

Expected start (s)
    (Optional) expected start (s), purely for representing in the timeline

Expected duration (s)
    (Optional) expected duration (s), purely for representing in the timeline

Marker ID
    The ID of the AprilTag marker to display
    
    Options:
    - 0
    - 512

Data
===============================

Save onset/offset times
    Store the onset/offset times in the data file (as well as in the log file).

Sync timing with screen refresh
    Synchronize times with screen refresh (good for visual stimuli and responses based on them)

Layout
===============================

Spatial units
    Units of dimensions for this stimulus
    
    Options:
    - from exp settings
    - deg
    - cm
    - pix
    - norm
    - height
    - degFlatPos
    - degFlat

Position [x,y]
    Position of this stimulus (e.g. [1,2] )

Size [w,h]
    Size of this stimulus (either a single value or x,y pair, e.g. 2.5, [1,2] 

Anchor
    Which point on the stimulus should be anchored to its exact position?
    
    Options:
    - center
    - top-center
    - bottom-center
    - center-left
    - center-right
    - top-left
    - top-right
    - bottom-left
    - bottom-right

Appearance
===============================

Contrast
    Contrast of the stimulus (1.0=unchanged contrast, 0.5=decrease contrast, 0.0=uniform/no contrast, -0.5=slightly inverted, -1.0=totally inverted)

Testing
===============================

Validate with...
    Name of validator Component/Routine to use to check the timing of this stimulus.
    
    Options:
    - VisualValidatorRoutine

