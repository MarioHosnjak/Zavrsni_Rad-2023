# import the necessary packages
import numpy as np
import cv2

# create mouse global coordinates
x_mouse = 200
y_mouse = 150

# create thermal video fps variable (8 fps in this case)
fps = 8
 
# mouse events function
def mouse_events(event, x, y, flags, param):
    # mouse movement event
    if event == cv2.EVENT_MOUSEMOVE:
        # update global mouse coordinates
        global x_mouse
        global y_mouse
        x_mouse = x
        y_mouse = y

        # set up mouse events and prepare the thermal frame display
        gray16_frame = cv2.imread("./thermal_pics/sampletiff.tiff", cv2.IMREAD_ANYDEPTH)
        cv2.imshow('gray8', gray16_frame)
        cv2.setMouseCallback('gray8', mouse_events)
                
        # open the gray16 frame
        gray16_frame = cv2.imread("./thermal_pics/sampletiff.tiff", cv2.IMREAD_ANYDEPTH)

        # calculate temperature
        temperature_pointer = gray16_frame[y_mouse, x_mouse]
        temperature_pointer = (temperature_pointer / 100)# - 273.15
        #temperature_pointer = (temperature_pointer / 100) * 9 / 5 - 459.67

        # convert the gray16 frame into a gray8
        gray8_frame = np.zeros((120, 160), dtype=np.uint8)
        gray8_frame = cv2.normalize(gray16_frame, gray8_frame, 0, 255, cv2.NORM_MINMAX)
        gray8_frame = np.uint8(gray8_frame)
                
        # colorized the gray8 frame using OpenCV colormaps
        gray8_frame = cv2.applyColorMap(gray8_frame, cv2.COLORMAP_INFERNO)
        # write pointer
        cv2.circle(gray8_frame, (x_mouse, y_mouse), 2, (255, 255, 255), -1)
        # write temperature
        cv2.putText(gray8_frame, "{0:.1f} Celsius".format(temperature_pointer), (x_mouse - 40, y_mouse - 15), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        # show the thermal frame
        cv2.imshow("gray8", gray8_frame)


# set up mouse events and prepare the thermal frame display
gray16_frame = cv2.imread("./thermal_pics/sampletiff.tiff", cv2.IMREAD_ANYDEPTH)
cv2.imshow('gray8', gray16_frame)
cv2.setMouseCallback('gray8', mouse_events)
        
# open the gray16 frame
gray16_frame = cv2.imread("./thermal_pics/sampletiff.tiff", cv2.IMREAD_ANYDEPTH)

# calculate temperature
temperature_pointer = gray16_frame[y_mouse, x_mouse]
temperature_pointer = (temperature_pointer / 100) - 273.15
#temperature_pointer = (temperature_pointer / 100) * 9 / 5 - 459.67

# convert the gray16 frame into a gray8
gray8_frame = np.zeros((120, 160), dtype=np.uint8)
gray8_frame = cv2.normalize(gray16_frame, gray8_frame, 0, 255, cv2.NORM_MINMAX)
gray8_frame = np.uint8(gray8_frame)
        
# colorized the gray8 frame using OpenCV colormaps
gray8_frame = cv2.applyColorMap(gray8_frame, cv2.COLORMAP_INFERNO)
# write pointer
cv2.circle(gray8_frame, (x_mouse, y_mouse), 2, (255, 255, 255), -1)
# write temperature
cv2.putText(gray8_frame, "{0:.1f} Celsius".format(temperature_pointer), (x_mouse - 40, y_mouse - 15), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
# show the thermal frame
cv2.imshow("gray8", gray8_frame)
# wait 125 ms: RGMVision ThermalCAM1 frames per second = 8
#cv2.waitKey(int((1 / fps) * 100000))
cv2.waitKey(0)
cv2.destroyAllWindows()