import cv2
import numpy as np
import time
import aerodiode as ae

def main():
    dev = ae.Pdmv3('COM4')
    status = dev.read_status_instruction(dev.INSTRUCT_READ_INTERLOCK_STATUS)
    print(status)
    current = dev.read_current_instruction(dev.INSTRUCT_MAX_MEAN_CURRENT)
    print(current)
    c=dev.set_current_instruction(dev.INSTRUCT_CURRENT_PERCENT,60.0)
    print(c)

    cap = cv2.VideoCapture(0)
    back_sub = cv2.createBackgroundSubtractorMOG2(history=700,varThreshold=25, detectShadows=True)
    kernel = np.ones((20,20),np.uint8)

    while(True):
        ret, frame = cap.read()
        fg_mask = back_sub.apply(frame)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        fg_mask = cv2.medianBlur(fg_mask, 5)
        _, fg_mask = cv2.threshold(fg_mask,127,255,cv2.THRESH_BINARY)
        fg_mask_bb = fg_mask
        contours, hierarchy = cv2.findContours(fg_mask_bb,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2:]
        areas = [cv2.contourArea(c) for c in contours]
        if len(contours) > 0:
            areas = [cv2.contourArea(c) for c in contours]
            max_index = np.argmax(areas)
            cnt = contours[max_index]
            x,y,w,h = cv2.boundingRect(cnt)
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),3)
            x2 = x + int(w/2)
            y2 = y + int(h/2)
            cv2.circle(frame,(x2,y2),4,(0,255,0),-1)
            text = "x: " + str(x2) + ", y: " + str(y2)
            cv2.putText(frame, text, (x2 - 10, y2 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            intrusion_detected = False
            if max(areas) > 10000:
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
                print(f"No intrusion detected at {time.strftime('%H:%M:%S', time.localtime())}")

        else:
            
            dev.set_status_instruction(dev.INSTRUCT_LASER_ACTIVATION, dev.ON)
            dev.apply_all()
            print(f"No intrusion detected at {time.strftime('%H:%M:%S', time.localtime())}")

        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()