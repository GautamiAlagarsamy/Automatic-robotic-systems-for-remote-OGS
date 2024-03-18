import sys
import numpy as np
import aerodiode as ae
from time import sleep
import time
dev = ae.Pdmv3('COM4')
status = dev.read_status_instruction(dev.INSTRUCT_READ_INTERLOCK_STATUS)
print(status)
current = dev.read_current_instruction(dev.INSTRUCT_MAX_MEAN_CURRENT)
print(current)
c=dev.set_current_instruction(dev.INSTRUCT_CURRENT_PERCENT,60.0)
print(c)

def process_measurements(measurements):
    
    # Turn on the laser if there are no detections
    if measurements.size == 0:
        dev.set_status_instruction(dev.INSTRUCT_LASER_ACTIVATION, dev.ON)
        dev.apply_all()
        print("Laser turned on")
    else:
        # Turn off the laser if there are detections
        dev.set_status_instruction(dev.INSTRUCT_LASER_ACTIVATION, dev.OFF)
        dev.apply_all()
        print("Laser turned off")






if __name__ == "__main__":
    measurements = sys.argv[1:]
    measurements = np.array(measurements, dtype=float).reshape(-1, 3)
    process_measurements(measurements)
    time.sleep(1)