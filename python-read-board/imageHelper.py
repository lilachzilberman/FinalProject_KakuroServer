import cv2
from pylab import *
import pylab as pl
import matplotlib.pyplot as plt

def convertToGray(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def convertToColor(image):
    return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

def drawLine(image, start, end, color, colorWidth):
    cv2.line(image, (start[0], start[1]), (end[0], end[1]), color, colorWidth)
    return

def putText(image, point, text):
    cv2.putText(image, text, point, cv2.FONT_HERSHEY_SIMPLEX, 2, (255,0,0), 5)
    return

def show(image, title=None):
    #show image
    # _=pl.axis("off")
    # if (title != None):
    #     _=pl.title(title)
    # _ = pl.imshow(image, cmap=pl.gray())
    # plt.show()
    return
