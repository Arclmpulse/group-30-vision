# Version 1.0

Initial code to set up camera and for basic object detection.

Camera being used is an Intel RealSense Depth Camera D415. Will keep using this unless it becomes infeasible.

YOLOv4 and opencv-python will be used as a proof of concept. Might upgrade to YOLOv8 if this won't cut it, we'll see. Less documentation on that but it is more efficient so...

## Naming convention
When a major function is introduced to the code or massively revamped ie. Thresholding algorithms, Filters, adding new libraries etc. Change the first digit of the version! (1.0 -> 2.0)

When only existing code/functions have been changed ie. Adding QoL changes like a framerate counter or adjusting values, bug fixing, etc. Change the second digit of the version!

Please add all edits to changelog, I'd like to know which version of code is stable and we can squash bugs faster that way.

## Installation (for dummies!)
This will be assuming pip is installed.

### Libraries
Install numpy, opencv-python, tensorflow, and yolov4.

### Other Files
You will also need to download a file from the following link: https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights

Please install this to the directory of the other files!

Open IDE of choice and run the python script.

## Known Bugs
CPU/Memory allocation is a little uncontrolled, may crash other programs. Will look into this.


## Changelog
### Version 1.0
Script sucessfully pulls camera.
