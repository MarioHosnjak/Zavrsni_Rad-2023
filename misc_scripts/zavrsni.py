import cv2
import numpy as np

#Open thermal image for temperatures
gray16_frame = cv2.imread("./recog_pics/pic1.jpg", cv2.IMREAD_ANYDEPTH)

img = cv2.imread('./recog_pics/pic1.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blr = cv2.GaussianBlur(gray, (5, 5), 0)
thr = cv2.adaptiveThreshold(blr, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 65, 17)
contours,hierarchy = cv2.findContours(thr, 1, 2)
#cv2.imshow("thresh", thr)

n = 0
for cnt in contours:
   x1,y1 = cnt[0][0]
   approx = cv2.approxPolyDP(cnt, 0.05*cv2.arcLength(cnt, True), True)
   if len(approx) == 4:
      x, y, w, h = cv2.boundingRect(cnt)
      if w >= 40 and w < img.shape[1] and h < img.shape[0]:
        ratio = float(w)/h
        n = n+1
        if ratio >= 0.85 and ratio <= 1.15:
            img = cv2.drawContours(img, [cnt], -1, (0,255,255), 3)
            cv2.putText(img, f'Square {n}', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        else:
            cv2.putText(img, f'Rectangle {n}', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            img = cv2.drawContours(img, [cnt], -1, (255,255,0), 3)
        # READ TEMPERATURE
        print(f"Object: {n}")
        xt, yt, wt, ht = cv2.boundingRect(cnt)
        maxTemp = [0, 0, 0]
        for i in range(xt, xt + wt):
            for j in range(yt, yt + ht):
                temperature_pointer = gray16_frame[j, i]
                temperature_pointer = (temperature_pointer / 100)
                if temperature_pointer > maxTemp[0]:
                    maxTemp = [temperature_pointer, i, j]
                #print(f"Pixel coordinates: ({i}, {j}) Temp: {temperature_pointer}")
                #cv2.circle(img, (i, j), 1, (255, 255, 255), -1)
        print(f"Max temp for object {n} is {maxTemp[0]}°C x={maxTemp[1]} y={maxTemp[2]}")
        cv2.circle(img, (maxTemp[1], maxTemp[2]), 5, (255, 255, 255), -1)

cv2.imshow("Shapes", img)
cv2.waitKey(0)
cv2.destroyAllWindows()