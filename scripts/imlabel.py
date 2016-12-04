#! /usr/bin/python

import os
import sys
import copy
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

imageDir = '../rs_resize_pics/tiled/'
picRange = (1,5)

if picRange[1] < picRange[0]:
  print "Fix picRange so that first entry is >= second entry"
  sys.exit(1)

for currRGB in os.listdir(imageDir):
  currRGBSplit = currRGB.split('_')
  currPicNum = (currRGBSplit[0])[3:]
  if os.path.isfile(imageDir + currRGB) and \
    currRGB != '.DS_Store' and \
    currRGBSplit[1] == 'rgb' and \
    currRGBSplit[2] == 'res' and \
    int(currPicNum) >= picRange[0] and \
    int(currPicNum) <= picRange[1]:
    print 'Now labeling', currRGB
    image = mpimg.imread(imageDir + currRGB)
    plt.imshow(image)
    plt.draw()
    plt.pause(1)
    raw_input()
    plt.close()

    validLabel = False
    while not validLabel:
      label = raw_input('Enter the image label: ')
      print label
      if label != str(0) and label != str(1) and label != 'u':
        print 'Invalid label', label, ', try again'
      else:
        print currRGB, 'was labeled as', label
        validLabel = True

    # Find corresponding depth image
    depthIm = currRGB.replace('rgb', 'd')
    newRGB = currRGB.replace('res', label)
    newDepth = newRGB.replace('rgb', 'd')
    os.rename(imageDir + currRGB, imageDir + newRGB)
    os.rename(imageDir + depthIm, imageDir + newDepth)

print 'Done'