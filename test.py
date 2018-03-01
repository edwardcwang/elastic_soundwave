#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  test.py

from backend import *

from tone_generator import ToneGenerator

import collections
import sys

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim

MAX_X = 400

#~ MIN_Y = 0 # pressure sensor

# Side furtherest away from LaunchPad

leftmost_sensor = (12.10e3, 12.23e3, True)

upper_left_sensor = (11.70e3, 11.75e3, False)

center_sensor = (10.765e3, 10.865e3, False)

upper_right_sensor = (12.09e3, 12.14e3, False) # third parameter is True if reversed

rightmost_sensor = (11.25e3, 11.305e3, False)

CURRENT_SENSOR = center_sensor

(MIN_Y, MAX_Y, _) = CURRENT_SENSOR

xlims = np.arange(-MAX_X//2, MAX_X//2)

def update(fn, l2d, ser, line, data, num_read):
    # try:
    #~ d = ser.read_int()
    for i in range(num_read):
        #~ base = i*2
        #~ data[i] = (d[base] & 63) * 64 + (d[base+1] & 63)
        data[i] = ser.read_int()
        print(data[i])
    #logger.debug("Raw ADC value: %s"%data)

    # Add new point to deque
    line[:-num_read] = line[num_read:]
    line[-num_read:] = data/4096
    # line.append(float(data)/4096)

    # Set the l2d to the new line coord ([x-coords], [y-coords])
    l2d.set_data(xlims, line)

def find_resistance(V: float, V_fs: float, R_ref: float):
    """
    Given a voltage reading where V = V_fs* R_target/(R_target + R_ref), find R_target.
    """
    return R_ref*V/(V_fs - V)

import time

R_ref_10 = 11.883e3

R_ref_pressure = 9.83e3 # 10k
R_ref_flex = 39.33e3 # 40k

my_count = 0
def get_count():
    global my_count
    my_count += 1
    return my_count

def average():
    pass

def clamp(minimum, x, maximum):
    return max(minimum, min(x, maximum))

def calc_percent(data, sensor):      
    if data > sensor[1]:
        data_clamped = sensor[1]
    elif data < sensor[0]:
        data_clamped = sensor[0]
    else:
        data_clamped = data
    #~ data_clamped = clamp(sensor[0], data, sensor[1])
    percent = (data_clamped - sensor[0])/(sensor[1] - sensor[0])
    if sensor[2]:
        return 1.0 - percent
    else:
        return percent

def major_scale(frac):
    #~ fracs = np.array([0, 2, 4, 5, 7, 9, 11, 12])
    fracs = np.array([0, 2, 4, 5, 7, 9, 11, 12,    12, 14, 16, 17, 19, 21, 23, 24])
    bins = np.linspace(0, 1, len(fracs))
    return fracs[np.digitize(frac, bins, right=True)]/12

def main(args):
    ser = SerialBackend(args[1], 115200)

    tone = ToneGenerator()
    tone.set_sampling_info(22050, 2)
    tone.samples = tone.create_sine_generator()
    tone.start_audio_thread()

    plt.ion()
    fig = plt.figure(figsize=(9.5, 7))

    # make the axes revolve around [0,0] at the center
    # instead of the x-axis being 0 - +100, make it -50 - +50 ditto
    # for y-axis -512 - +512
    a = plt.axes(xlim=(-(MAX_X/2),MAX_X/2),ylim=(MIN_Y,MAX_Y) if MAX_Y is not None else None)
    num_read = 4

    line = np.zeros(dtype=np.float32, shape=(MAX_X))
    data = np.zeros(dtype=np.float32, shape=(num_read))

    # plot an empty line and keep a reference to the line2d instance
    l1, = a.plot([], [])
    #~ ani = anim.FuncAnimation(fig, update, fargs=(l1, ser, line, data, num_read), interval=0.001*num_read)
    plt.title("ADC output")
    plt.xlabel("t")
    plt.show()

    R_ref = R_ref_10
    
    data_buffer = collections.deque(maxlen=256)

    while True:
        for i in range(num_read):
            def read_fn():
                datas = find_resistance(float(ser.read_int()), 4096.0, R_ref)
                # Also enqueue in buffer
                data_buffer.append(datas)
                return datas
            def read_fn2():
                while True:
                    try:
                        return read_fn()
                    except ValueError:
                        continue
            #~ res = read_fn()
            
            # Sum
            res_sum = 0.0
            num_avg = 180
            #~ num_avg = 256
            for _ in range(num_avg):
                res_sum += read_fn2()
            res = res_sum / float(num_avg)
            
            data[i] = res
            #~ print("Measured resistance: ", res)


        data_buffer_mean = np.average(data_buffer)

        #~ data_avg = data_buffer_mean
        data_avg = np.average(data)
        
        data_percent = calc_percent(data_avg, CURRENT_SENSOR)
        
        # Apply major scale
        data_percent = major_scale(data_percent)
        tone_val = 523.25*(2**data_percent)
        tone.freq = tone_val

        full_buffer_percent = calc_percent(data_buffer_mean, CURRENT_SENSOR)
        full_buffer_byte = int(255*full_buffer_percent)
        if get_count() % 5 == 0:
            ser.write_raw_byte(full_buffer_byte)
            print("data_buffer_mean = " + str(data_buffer_mean) + ", data_percent = " + str(data_percent) + ", tone_val = " + str(tone_val) + ", full_buffer_percent = " + str(full_buffer_percent))

        # Add new point to deque
        line[:-num_read] = line[num_read:]
        line[-num_read:] = data

        l1.set_data(xlims, line)
        fig.canvas.draw()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
