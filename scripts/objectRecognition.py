import cv2
import numpy as np

img = cv2.imread('./recog_pics/pic1.jpg')
#img = cv2.imread('./thermal_pics/sample_32x24.tiff')
#img = cv2.imread('shapes.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Apply Gaussian-blur
blr = cv2.GaussianBlur(gray, (5, 5), 0)

#cv2.imshow("blur", blr)
#cv2.imshow("noblur", gray)

# Apply threshold
thr = cv2.adaptiveThreshold(blr, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 65, 17) #  IGRATI SE S ZADNJE DVIJE VRIJEDNOSTI

#invert
#thr = cv2.bitwise_not(thr)

#ret,thresh = cv2.threshold(blr,140,255,0)
contours,hierarchy = cv2.findContours(thr, 1, 2)
print("Number of contours detected:", len(contours))

cv2.imshow("thresh", thr)

i = 1
for cnt in contours:
   x1,y1 = cnt[0][0]
   approx = cv2.approxPolyDP(cnt, 0.05*cv2.arcLength(cnt, True), True)  #  IGRATI SE S DECIMALOM
   if len(approx) == 4:
      x, y, w, h = cv2.boundingRect(cnt)
      if w < 40:
          continue
      ratio = float(w)/h
      print(i)
      i = i+1
      if ratio >= 0.85 and ratio <= 1.15:
         img = cv2.drawContours(img, [cnt], -1, (0,255,255), 3)
         cv2.putText(img, 'Square', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
      else:
         cv2.putText(img, 'Rectangle', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
         img = cv2.drawContours(img, [cnt], -1, (255,255,0), 3)

cv2.imshow("Shapes", img)
#cv2.imshow("Shapes", cv2.resize(img, (320, 240)))
cv2.waitKey(0)
cv2.destroyAllWindows()