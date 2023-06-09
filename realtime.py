import cv2
import numpy as np
import math
import time
from PIL import Image
import board
import adafruit_mlx90640
import sys
import matplotlib.pyplot as plt
import csv

# if False -> MINTEMP = min temp., MAXTEMP = max temp, 
# if True -> MINTEMP = 0, MAXTEMP = 100
fixedMinMax = False
MIN_MAP_TEMP = 0.0  # low range of the sensor (deg C)
MAX_MAP_TEMP = 100.0 # high range of the sensor (deg C)
COLORDEPTH = 1000  # how many color values we can have
INTERPOLATE = 10  # scale factor for final image

mlx = adafruit_mlx90640.MLX90640(board.I2C())

mlx.refresh_rate = 5
print(f"Refresh rate = {mlx.refresh_rate}")

# the list of colors we can choose from
heatmap = (
    (0.0, (0, 0, 0)),
    (0.20, (0, 0, 0.5)),
    (0.40, (0, 0.5, 0)),
    (0.60, (0.5, 0, 0)),
    (0.80, (0.75, 0.75, 0)),
    (0.90, (1.0, 0.75, 0)),
    (1.00, (1.0, 1.0, 1.0)),
)

colormap = [0] * COLORDEPTH

# utility functions
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def gaussian(x, a, b, c, d=0):
    return a * math.exp(-((x - b) ** 2) / (2 * c**2)) + d

def gradient(x, width, cmap, spread=1):
    width = float(width)
    r = sum(gaussian(x, p[1][0], p[0] * width, width / (spread * len(cmap))) for p in cmap)
    g = sum(gaussian(x, p[1][1], p[0] * width, width / (spread * len(cmap))) for p in cmap)
    b = sum(gaussian(x, p[1][2], p[0] * width, width / (spread * len(cmap))) for p in cmap)
    r = int(constrain(r * 255, 0, 255))
    g = int(constrain(g * 255, 0, 255))
    b = int(constrain(b * 255, 0, 255))
    return r, g, b

for i in range(COLORDEPTH):
    colormap[i] = gradient(i, COLORDEPTH, heatmap)

try:
    counter = 0
    time = 0
    temp_list = []
    time_list = []
    fig, ax = plt.subplots()
    while True:
        # get sensor data
        frame = [0] * 768
        success = False
        while not success:
            try:
                mlx.getFrame(frame)
                success = True
            except ValueError:
                continue
        # create the image
        pixels = [0] * 768
        MINTEMP = frame[0]
        MAXTEMP = frame[0]
        for temp in frame:
            if temp > MAXTEMP:
                MAXTEMP = temp
            if temp < MINTEMP:
                MINTEMP = temp
        if fixedMinMax == False:
            MIN_MAP_TEMP = MINTEMP
            MAX_MAP_TEMP = MAXTEMP
        print("Maxtemp = ", MAXTEMP)
        if counter % 5 == 0:
            temp_list.append(MAXTEMP)
            time = time + 0.5
            time_list.append(time)
            ax.clear()
            ax.plot(time_list, temp_list, marker='o')
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Temperature (°C)')
            ax.set_title('Maximum temperature')
            plt.draw()
            plt.pause(0.01)
        counter = counter + 1
        for i, pixel in enumerate(frame):
            coloridx = map_value(pixel, MIN_MAP_TEMP, MAX_MAP_TEMP, 0, COLORDEPTH - 1)
            coloridx = int(constrain(coloridx, 0, COLORDEPTH - 1))
            pixels[i] = colormap[coloridx]
        img = Image.new("RGB", (32, 24))
        img.putdata(pixels)
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        img = img.resize((32 * INTERPOLATE, 24 * INTERPOLATE), Image.BICUBIC)
        image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        cv2.imshow('Video', image)
        cv2.waitKey(1)
except KeyboardInterrupt:
    plt.show()