import aerodiode as ae
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from time import sleep
from moku.instruments import Oscilloscope


dev = ae.Pdmv3('COM4')
status = dev.read_status_instruction(dev.INSTRUCT_READ_INTERLOCK_STATUS)
print(status)
current = dev.read_current_instruction(dev.INSTRUCT_MAX_MEAN_CURRENT)
print(current)
c=dev.set_current_instruction(dev.INSTRUCT_CURRENT_PERCENT,60.0)
print(c)

global avg_ch1, xs, prev_avg_ch1, WARNING_THRESHOLD
avg_ch1 = np.array([])
xs = np.array([])
prev_avg_ch1 = 0
WARNING_THRESHOLD = 0.1
def update(num):
    global i, data, avg_ch1, xs, prev_avg_ch1, WARNING_THRESHOLD
    data = i.get_data()
    ax[0].set_xlim(data['time'][0], data['time'][-1])
    ax[0].set_ylim(data['ch1'][0], data['ch2'][-1])
    avg_ch1 = np.append(avg_ch1, np.mean(data['ch1']))
    xs = np.append(xs, num)

    line1.set_data(data['time'], data['ch1'])
    line2.set_data(data['time'], data['ch2'])

    scatter1_data = np.array([xs, avg_ch1]).T
    scatter1.set_offsets(scatter1_data)

    ax[1].set_xlim(0, num)
    diff = np.abs(avg_ch1[-1] - prev_avg_ch1)
    prev_avg_ch1 = avg_ch1[-1]

    # check if the difference is greater than the threshold
    if diff > WARNING_THRESHOLD:
        print(f"Warning: Average value changed by {diff:.2f} V!")

        if np.mean(data['ch1']) <= WARNING_THRESHOLD:
            dev.set_status_instruction(dev.INSTRUCT_LASER_ACTIVATION, dev.OFF)
            dev.apply_all()
            sleep(4)
        else:
            dev.set_status_instruction(dev.INSTRUCT_LASER_ACTIVATION, dev.ON)
            dev.apply_all()
            sleep(3)

    else:
        dev.set_status_instruction(dev.INSTRUCT_LASER_ACTIVATION, dev.ON)
        dev.apply_all()

    return line1, line2, scatter1

i = Oscilloscope('192.168.73.1', force_connect=True)
fig, ax = plt.subplots(1, 2)
line1, = ax[0].plot([], [], label='Channel 1')
line2, = ax[0].plot([], [], label='Channel 2')
ax[0].set_xlabel('Time')
ax[0].set_ylabel('Voltage')
ax[0].legend()
scatter1 = ax[1].scatter([], [], color='red', marker='o')
ax[1].set_xlabel('Sample')
ax[1].set_ylabel('Average Voltage')
interval = 100
WARNING_THRESHOLD = 0.1
ani = FuncAnimation(fig, update, frames=np.arange(0, 1000, 1), cache_frame_data=False, interval=interval, blit=True)

plt.show()