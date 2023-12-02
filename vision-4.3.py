import cv2
import numpy as np
import pyrealsense2 as rs
import pandas as pd
from datetime import datetime, timedelta

def initialize_pipeline():
    # Initialize the RealSense pipeline
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 848, 480, rs.format.bgr8, 60)
    config.enable_stream(rs.stream.depth, 848, 480, rs.format.z16, 90)
    pipeline.start(config)
    return pipeline

def initialize_video_writer():
    # Define the codec and create a VideoWriter object with higher framerate and resolution
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # XVID codec
    return cv2.VideoWriter('output.avi', fourcc, 60.0, (848, 480))

def detect_faces(frame):
    # Load the pre-trained face detection model
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Convert the frame to grayscale for face detection
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

def process_frame(frame, color_frame, depth_frame, recording, out, xyz_data, last_record_time):
    try:
        # Convert the frame to grayscale for additional processing
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Update intrinsics for the new resolution (assuming these lines were outside the try block)
        color_intrinsics = color_frame.profile.as_video_stream_profile().intrinsics
        depth_intrinsics = depth_frame.profile.as_video_stream_profile().intrinsics

        # Detect faces in the frame
        detect_faces(frame)

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
                    depth_point = rs.rs2_deproject_pixel_to_point(
                        depth_intrinsics, [center_x, center_y], depth_value)

                    x_coord, y_coord, z_coord = depth_point

                    # Record XYZ coordinates only when recording is active
                    if recording:
                        # Append the coordinates to the list
                        current_time = datetime.now()
                        xyz_data.append({
                            'Timestamp': current_time,
                            'X_coord': x_coord,
                            'Y_coord': y_coord,
                            'Z_coord': z_coord
                        })

                        # Update the last recorded time
                        last_record_time = current_time

                    # Display coordinates on separate lines
                    cv2.putText(frame, f"Depth X: {x_coord:.3f} meters",
                                (center_x - radius, center_y + radius), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    cv2.putText(frame, f"Depth Y: {y_coord:.3f} meters",
                                (center_x - radius, center_y + radius + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    cv2.putText(frame, f"Depth Z: {z_coord:.3f} meters",
                                (center_x - radius, center_y + radius + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    except Exception as e:
        # Print the error message to the console
        print(f"Error in frame processing: {e}")

def main():
    # Initialize RealSense pipeline and video writer
    pipeline = initialize_pipeline()
    out = initialize_video_writer()

    # Flag to track whether recording is active
    recording = False

    # Create an empty list to store data
    xyz_data = []

    # Timestamp for the last recorded frame
    last_record_time = datetime.now()

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

            # Process the frame
            process_frame(frame, recording, out, xyz_data, last_record_time)

            # Check for key press
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                break  # Close the OpenCV window and exit the loop
            elif key == ord('r'):
                # Toggle recording on/off
                if recording:
                    out.release()  # Stop recording
                    recording = False

                    # Convert the list to a DataFrame
                    xyz_df = pd.DataFrame(xyz_data)

                    # Save the DataFrame to an Excel file when recording is stopped
                    xyz_df.to_excel('xyz_coordinates.xlsx', index=False)
                else:
                    out = initialize_video_writer()  # Start recording
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

if __name__ == "__main__":
    main()
