import cv2
import math
import yaml
import csv
import time
from datetime import datetime
from ultralytics import YOLO
import aerodiode as ae

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


# initialize laser
dev = ae.Pdmv3('COM4')
status = dev.read_status_instruction(dev.INSTRUCT_READ_INTERLOCK_STATUS)
print(status)
current = dev.read_current_instruction(dev.INSTRUCT_MAX_MEAN_CURRENT)
print(current)
c=dev.set_current_instruction(dev.INSTRUCT_CURRENT_PERCENT,60.0)
print(c)

# set confidence threshold
conf_thresh = 0.5
# flag to track if laser should be on or off
laser_on = True



# time to wait before turning laser back on after no detections
no_detection_timeout = 10  # seconds
start_time = time.time()

while True:
    success, img = cap.read()
    results = model(img, stream=True)

    intrusion_detected= False
    intrusion_time = time.time()

    # coordinates
    for r in results:
        boxes = r.boxes

        for box in boxes:
            # bounding box
            x1, y1, x2, y2= box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)  # convert to int values

            # confidence
            confidence = math.ceil((box.conf[0] * 100)) / 100
            print("Confidence --->", confidence)
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

            
                intrusion_detected = True
                intrusion_time = time.time()
                status = dev.read_status_instruction(dev.INSTRUCT_READ_INTERLOCK_STATUS)
                if intrusion_detected == True and status == 1:
                    dev.set_status_instruction(dev.INSTRUCT_LASER_ACTIVATION, dev.OFF)
                    dev.apply_all()
                    print(f"Intrusion detected at {time.strftime('%H:%M:%S', time.localtime())}. Time taken: {time.time() - intrusion_time} seconds")

                elif intrusion_detected == True and status == 0:
                    dev.set_status_instruction(dev.INSTRUCT_LASER_ACTIVATION, dev.OFF)
                    dev.apply_all()
                    print(f"Intrusion detected at {time.strftime('%H:%M:%S', time.localtime())}. Time taken: {time.time() - intrusion_time} seconds")
            else:
                dev.set_status_instruction(dev.INSTRUCT_LASER_ACTIVATION, dev.ON)
                dev.apply_all()
                laser_on = True
                print(f"No intrusion detected at {time.strftime('%H:%M:%S', time.localtime())}")

    cv2.imshow('Webcam', img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()