import aerodiode as ae
from time import sleep

dev = ae.Pdmv3('COM4')
status = dev.read_status_instruction(dev.INSTRUCT_READ_INTERLOCK_STATUS)
print(status)
current = dev.read_current_instruction(dev.INSTRUCT_MAX_MEAN_CURRENT)
print(current)
c=dev.set_current_instruction(dev.INSTRUCT_CURRENT_PERCENT,60.0)
print(c)
while True:
    status = dev.read_status_instruction(dev.INSTRUCT_READ_INTERLOCK_STATUS)
    if status == 1:
        dev.set_status_instruction(dev.INSTRUCT_LASER_ACTIVATION, dev.OFF)
        dev.apply_all()
    elif status == 0:
        laser_status = dev.read_status_instruction(dev.INSTRUCT_LASER_ACTIVATION)
        if laser_status == dev.OFF:
            dev.set_status_instruction(dev.INSTRUCT_LASER_ACTIVATION, dev.ON)
            dev.apply_all()
    sleep(1)

