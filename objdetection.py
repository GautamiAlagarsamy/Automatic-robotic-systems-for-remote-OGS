import cv2
import numpy as np
import csv
import time
from datetime import datetime

# Initialize the webcam
cap = cv2.VideoCapture(0)

# Define the background subtractor
fgbg = cv2.createBackgroundSubtractorMOG2()

# Initialize the background image of the sky
background = None



# Open the CSV file in write mode
with open('detection.csv', 'w', newline='') as csvfile:
    # Create a CSV writer object
    writer = csv.writer(csvfile)

    # Write the header row
    writer.writerow(['Object', 'Time In', 'Time Out', 'Time Diff (s)'])

    while True:
        # Capture the next frame from the webcam
        ret, frame = cap.read()

        # Crop the frame to the region of interest (ROI) where the sky is located
        roi = frame[100:400, 0:640]

        # If the background image is not initialized, initialize it with the current ROI
        if background is None:
            background = roi.copy()
            continue

        # Apply background subtraction to the ROI
        fgmask = fgbg.apply(roi, learningRate=0.01)

        # Dilate the foreground mask to close small gaps between object contours
        fgmask = cv2.dilate(fgmask, np.ones((10,10),np.uint8),iterations=2)

        # Find contours in the foreground mask
        contours, hierarchy = cv2.findContours(fgmask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Draw rectangles around the detected objects
        for contour in contours:
            x,y,w,h = cv2.boundingRect(contour)
            # Filter out small contours
            if w < 10 or h < 10:
                continue
            cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Record the time in for the detected object
            time_in = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            cv2.putText(roi, time_in, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Calculate the time difference between time_out and time_in
            start_time = datetime.now()

            # Wait for a short period of time to record the time out
            # time.sleep(1)

            # Record the time out for the detected object
            time_out = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            cv2.putText(roi, time_out, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            # Calculate the time difference between time_out and time_in
            time_diff = datetime.now() - start_time

            # Write the data to the CSV file
            writer.writerow([f'Object {len(contours)}', time_in, time_out, time_diff])

        # Crop the frame to have the same dimensions as the background image
        frame_roi = frame[100:400, 0:640]

        # Update the background image with the current ROI
        background = cv2.addWeighted(background, 0.99, frame_roi, 0.01, 0)

        # Display the output frame
        cv2.imshow('Output', np.concatenate((roi[:,:,0], fgmask), axis=0))

        # Exit if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()