import cv2
import numpy as np
import math
import time
from PIL import Image
import board
import adafruit_mlx90640

# if False -> MINTEMP = min temp., MAXTEMP = max temp, 
# if True -> MINTEMP = 0, MAXTEMP = 100
fixedMinMax = False
MINTEMP = 0.0  # low range of the sensor (deg C)
MAXTEMP = 100.0 # high range of the sensor (deg C)
COLORDEPTH = 1000  # how many color values we can have
INTERPOLATE = 10  # scale factor for final image

mlx = adafruit_mlx90640.MLX90640(board.I2C())

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
if fixedMinMax == False:
	MINTEMP = frame[0]
	MAXTEMP = frame[0]
	for temp in frame:
		if temp > MAXTEMP:
			MAXTEMP = temp
		if temp < MINTEMP:
			MINTEMP = temp
print("Mintemp = ", MINTEMP)
print("Maxtemp = ", MAXTEMP)
for i, pixel in enumerate(frame):
    coloridx = map_value(pixel, MINTEMP, MAXTEMP, 0, COLORDEPTH - 1)
    coloridx = int(constrain(coloridx, 0, COLORDEPTH - 1))
    pixels[i] = colormap[coloridx]
# create image and save to file
img = Image.new("RGB", (32, 24))
img.putdata(pixels)
img = img.transpose(Image.FLIP_TOP_BOTTOM)
img = img.resize((32 * INTERPOLATE, 24 * INTERPOLATE), Image.BICUBIC)
img.save("ir.jpg")
img.show()

############################################################################
# Object recognition

img = cv2.imread('./ir.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blr = cv2.GaussianBlur(gray, (5, 5), 0)
thr = cv2.adaptiveThreshold(blr, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 65, 17)
#cv2.imshow("Thr", thr)
contours,hierarchy = cv2.findContours(thr, 1, 2)

n = 0
for cnt in contours:
	x1,y1 = cnt[0][0]
	approx = cv2.approxPolyDP(cnt, 0.05*cv2.arcLength(cnt, True), True)
	if len(approx) == 4:
		x, y, w, h = cv2.boundingRect(cnt)
		if w >= 20: # and w < img.shape[1] and h < img.shape[0]:
			ratio = float(w)/h
			n = n+1
			if ratio >= 0.85 and ratio <= 1.15:
				img = cv2.drawContours(img, [cnt], -1, (0,255,255), 3)
				cv2.putText(img, f'Square {n}', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
			else:
				cv2.putText(img, f'Rectangle {n}', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
				img  = cv2.drawContours(img, [cnt], -1, (255,255,0), 3)
			# READ TEMPERATURE
			print(f"Object: {n}")
			xt, yt, wt, ht = cv2.boundingRect(cnt)
			maxTemp = [0, 0, 0]
			for i in range(xt, xt + wt):
				for j in range(yt, yt + ht):
					temperature_pointer = frame[int(j / 10) * 32 + int(i / 10)]
					if temperature_pointer > maxTemp[0]:
						maxTemp = [temperature_pointer, i, j]
			print(f"Max temp for object {n} is {maxTemp[0]}°C x={maxTemp[1]} y={maxTemp[2]}")
			cv2.circle(img, (maxTemp[1], maxTemp[2]), 5, (0, 0, 0), -1)

cv2.imshow("Shapes", img)
cv2.waitKey(0)
cv2.destroyAllWindows()