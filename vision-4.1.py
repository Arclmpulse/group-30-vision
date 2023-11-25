import cv2
import numpy as np
import pyrealsense2 as rs

# Load the pre-trained face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Initialize the RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 848, 480, rs.format.bgr8, 60)
config.enable_stream(rs.stream.depth, 848, 480, rs.format.z16, 90)

# Start the RealSense pipeline
pipeline.start(config)

# Define the codec and create a VideoWriter object with higher framerate and resolution
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # XVID codec
out = None  # VideoWriter object

recording = False  # Flag to track whether recording is active

# ...

while True:
    try:
        # Wait for the next set of frames from the RealSense camera
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()

        if not color_frame or not depth_frame:
            continue

        # Convert RealSense frames to OpenCV format
        frame = np.asanyarray(color_frame.get_data())

        # Convert the frame to grayscale for face detection
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Update intrinsics for the new resolution
        color_intrinsics = color_frame.profile.as_video_stream_profile().intrinsics
        depth_intrinsics = depth_frame.profile.as_video_stream_profile().intrinsics

        try:
            # Detect faces in the frame
            faces = face_cascade.detectMultiScale(
                gray_frame, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

            for (x, y, w, h) in faces:
                # Filter out detected faces by drawing rectangles (you can also choose to skip the frame)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # Apply Gaussian blur to reduce noise and improve edge detection
            blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)

            # Use Hough Circle Transform for circle detection
            circles = cv2.HoughCircles(blurred_frame, cv2.HOUGH_GRADIENT,
                                       dp=1, minDist=50, param1=100, param2=30, minRadius=30, maxRadius=50)

            if circles is not None:
                circles = np.uint16(np.around(circles))
                for circle in circles[0, :]:
                    center_x, center_y = circle[0], circle[1]
                    radius = circle[2]

                    # Calculate circularity manually
                    area = np.pi * (radius ** 2)
                    perimeter = 2 * np.pi * radius
                    circularity = 4 * np.pi * area / (perimeter ** 2)

                    # Filter by circularity and size
                    if 0.99 < circularity < 1.01 and radius > 10:
                        cv2.circle(frame, (center_x, center_y),
                                   radius, (0, 255, 0), 2)

                        # Measure the distance to the circle in meters
                        depth_value = depth_frame.get_distance(center_x, center_y)

                        # Map pixel coordinates to real-world coordinates
                        color_point = rs.rs2_deproject_pixel_to_point(
                            color_intrinsics, [center_x, center_y], depth_value)
                        depth_point = rs.rs2_deproject_pixel_to_point(
                            depth_intrinsics, [center_x, center_y], depth_value)

                        x_coord, y_coord, z_coord = depth_point

                        # Display coordinates on separate lines
                        cv2.putText(frame, f"Depth X: {x_coord:.3f} meters",
                                    (center_x - radius, center_y + radius), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        cv2.putText(frame, f"Depth Y: {y_coord:.3f} meters",
                                    (center_x - radius, center_y + radius + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        cv2.putText(frame, f"Depth Z: {z_coord:.3f} meters",
                                    (center_x - radius, center_y + radius + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        except Exception as e:
            # Print the error message to the console
            print(f"Error in circle detection: {e}")

        # Check for key press
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break  # Close the OpenCV window and exit the loop
        elif key == ord('r'):
            # Toggle recording on/off
            if recording:
                out.release()  # Stop recording
                recording = False
            else:
                out = cv2.VideoWriter(
                    'output.avi', fourcc, 60.0, (848, 480))  # Start recording with default RealSense resolution and framerate
                recording = True

        # Write the frame to the output video file if recording
        if recording:
            out.write(frame)

        # Display the processed frame
        cv2.imshow("Object Tracking", frame)

    except Exception as e:
        # Print the error message to the console
        print(f"Error in main loop: {e}")

# Release the video capture, RealSense pipeline, and writer objects
pipeline.stop()
if out is not None:
    out.release()
cv2.destroyAllWindows()
