# Version 4.3

Initial code to set up camera and for basic object detection.

Camera being used is an Intel RealSense Depth Camera D415. Will keep using this unless it becomes infeasible.

RealSense and opencv-python will be used as a proof of concept. Might use YOLOV8 if this won't cut it and if there's time to switch to DeepLearning, we'll see. Less documentation on that but it is more efficient.

Will compartmentalize and clean up later.

## Naming convention
When a major function is introduced to the code or massively revamped ie. Thresholding algorithms, Filters, adding new libraries etc. Change the first digit of the version! (1.0 -> 2.0)

When only existing code/functions have been changed ie. Adding QoL changes like a framerate counter or adjusting values, bug fixing, etc. Change the second digit of the version!

Please add all edits to changelog, I'd like to know which version of code is stable and we can squash bugs faster that way.

## Installation (for dummies!)
This will be assuming pip is installed.

### Libraries
Install numpy, opencv-python, ~~tensorflow~~, openpyxl, pyrealsense2 and ultralytics.

### Other Files
~~You will also need to download a file from the following link: https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights~~ Deprecated, may come back to it.

Please install [Realsense Viewer](https://github.com/IntelRealSense/librealsense/releases/tag/v2.54.2). If you need to adjust resolutions and framerate, as well as calibrate the camera, you can use this software to do so safely. It also provides a 3D viewer with the depth sensor - can use this to cross reference and debug incorrect values.

Open IDE of choice and run the python script.

## Known Bugs
~~CPU/Memory allocation is a little uncontrolled, may crash other programs. Will look into this.~~ Fixed!

~~Threshold is too loose on circular objects, will refine further.~~ Tightened threshold on circular objects, mostly fixed. Need to fine tune.

~~_Not detecting correct camera if multiple plugged in_ Not a bug. May look into updating code and retrieving the correct camera every single time.~~ Fixed!

_Motion is not perfect. Does not track high speed movement well._ It's better, not perfect.

~~Need more accurate focal length + depth of field for output. Incorrect values.~~ Fixed!

Sometimes, the camera feed won't exit properly. Not sure why

## Changelog
### Version 4.3
Compartmentalized the code a bit more.

### Version 4.2
Added a spreadsheet function to the record function for debugging.

### Version 4.1
Changed resolution, loosened the thresholding for detecting round objects. Will play around with it later to fix it once it's mounted, though it seems to work very well for a tennis ball.

Added some little changes to fix motion, can detect rolling objects at a slow speed reasonably well. Will need to fix better later once I understand the particle filter, might ask Kevin to just implement his.

Some other bugs came up, will fix later. Need to compartmentalize too.

### Version 4.0
Switched to Intel's SDK, fixed sensor issues with XYZ coordinates. Accuracy seems to be extremely high.

Added a record function with a hotkey, will output to directory.

Objects in motion are able to be detected better, but it's still not perfect.

### Version 3.0
Successfully outputs objects XYZ coordinate based off the given focal length. 

Fixed bugs related to circular objects getting detected too easily.

### Version 2.0
Fixed bugs related to crashing.

Successfully detects circular objects in real-time.

### Version 1.0
Script sucessfully pulls camera.


