import cv2
import numpy as np

# Load the pre-trained face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Initialize the USB camera (in this case, camera index 2)
cap = cv2.VideoCapture(0)

# Known parameters (from camera calibration)
focal_length = 1000  # Example focal length in pixels
real_object_height = 0.1  # Example real object height in meters (10 centimeters)

while True:
    ret, frame = cap.read()  # Read a frame from the camera

    # Convert the frame to grayscale for face detection
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        # Filter out detected faces by drawing rectangles (you can also choose to skip the frame)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # Apply Gaussian blur to reduce noise and improve edge detection
    blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)

    # Use Hough Circle Transform for circle detection
    circles = cv2.HoughCircles(blurred_frame, cv2.HOUGH_GRADIENT, dp=1, minDist=20, param1=100, param2=50, minRadius=25, maxRadius=75)

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
            if 0.99 < circularity < 1.01 and radius > 25:
                cv2.circle(frame, (center_x, center_y), radius, (0, 255, 0), 2)
                cv2.putText(frame, "Circle", (center_x, center_y - radius - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Measure the distance to the circle in meters
                object_height_in_pixels = 2 * radius  # Example: Use the object's diameter as its height
                distance = (real_object_height * focal_length) / object_height_in_pixels
                
                # Calculate distances from the top-left corner (X and Y) in meters
                distance_x = (center_x * real_object_height) / object_height_in_pixels
                distance_y = (center_y * real_object_height) / object_height_in_pixels
                
                cv2.putText(frame, f"Distance X: {distance_x:.2f} meters", (center_x - radius, center_y + radius + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.putText(frame, f"Distance Y: {distance_y:.2f} meters", (center_x - radius, center_y + radius + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.putText(frame, f"Distance Z: {distance:.2f} meters", (center_x - radius, center_y + radius + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)                

    # Display the processed frame
    cv2.imshow("Object Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break  # Close the OpenCV window and exit the loop

cap.release()
cv2.destroyAllWindows()
