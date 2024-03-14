import cv2
import math
import yaml
import csv
from datetime import datetime
from ultralytics import YOLO

# load classes from YAML file
with open("C:/Users/Gautami/Downloads/ultralytics-main/ultralytics-main/ultralytics/cfg/datasets/coco.yaml", "r", encoding="utf-8") as file:
    classes = yaml.safe_load(file)["names"]

# start webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# model
model = YOLO("yolov8n.pt")

# create CSV file
csv_file = "intrusion_log.csv"
with open(csv_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Object Name", "Time", "Date"])

# set confidence threshold
conf_thresh = 0.5

while True:
    success, img = cap.read()
    results = model(img, stream=True)

    # coordinates
    for r in results:
        boxes = r.boxes

        for box in boxes:
            # bounding box
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)  # convert to int values

            # confidence
            confidence = math.ceil((box.conf[0] * 100)) / 100

            # class name
            cls = int(box.cls[0])
            print("Class name -->", classes[cls])

            # object details
            org = (x1, y1)
            font = cv2.FONT_HERSHEY_SIMPLEX
            fontScale = 1
            color = (255, 0, 255)
            thickness = 2

            # draw bounding box and class name only if confidence is above threshold
            if confidence > conf_thresh:
                cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)
                cv2.putText(img, classes[cls], org, font, fontScale, color, thickness, cv2.LINE_AA)

                # log intrusion object details to CSV file
                with open(csv_file, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([classes[cls], datetime.now().strftime("%H:%M:%S"), datetime.now().strftime("%Y-%m-%d")])
                print("Intrusion detected")

    cv2.imshow('Webcam', img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()