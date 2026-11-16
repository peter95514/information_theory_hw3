import cv2
import numpy as np
import os

root = os.path.join(os.path.dirname(os.path.dirname(__file__)))
data = os.path.join(root, "data/")
color_image = os.path.join(data, "lena.png")

color = cv2.imread(color_image)

if color is None:
    raise FileNotFoundError("cant found lena.png")

gray = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)
cv2.imwrite(os.path.join(data, "lena_gray.png"), gray)
