import cv2
import numpy as np

# This script was used to programmatically find the exact pixel coordinates
# of the circular placeholders on the new map background (assets/map/new-map.png).
# It uses OpenCV's HoughCircles to detect them and logs the coordinates so they
# can be used to update map_sections.json.

# Load image
img = cv2.imread('../assets/map/new-map.png')
output = img.copy()
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Apply blur to reduce noise
gray = cv2.medianBlur(gray, 5)

# Detect exactly the 11 large target circles with thick borders.
# Tuned parameters specifically to isolate the 11 map nodes without noise.
circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=100,
                           param1=50, param2=45, minRadius=40, maxRadius=60)

coords = []

if circles is not None:
    circles = np.uint16(np.around(circles))

    # Sort left to right for consistency
    circle_list = list(circles[0, :])
    circle_list.sort(key=lambda c: c[0])

    for idx, i in enumerate(circle_list):
        coords.append((int(i[0]), int(i[1])))
        # draw the outer circle
        cv2.circle(output, (i[0], i[1]), i[2], (0, 255, 0), 2)
        # draw the center of the circle
        cv2.circle(output, (i[0], i[1]), 2, (0, 0, 255), 3)
        # put text label
        cv2.putText(output, str(idx), (i[0]-10, i[1]+10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    print("Found exactly {} circles.".format(len(coords)))
    for c in coords:
        print("x: {}, y: {}".format(c[0], c[1]))
    cv2.imwrite('circles_detected.png', output)
else:
    print("No circles found.")
