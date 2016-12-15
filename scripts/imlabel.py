#! /usr/bin/python

# Program to label images. Image will appear on-screen, and user can then
# close the image and label it as 0, 1, or u. Corresponding rgb, d, and
# ir (if applicable) files will be renamed to include appropriate label

import os
import sys
import copy
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

# Image directory and range of pictures to scan through
imageDir = '../rs-materials/rs_res_sr_pics/tiled/'
picRange = (10,10)

# Confirm picture range is valid
if picRange[1] < picRange[0]:
  print "Fix picRange so that first entry is >= second entry"
  sys.exit(1)

for currRGB in os.listdir(imageDir):
  currRGBSplit = currRGB.split('_')
  currPicNum = (currRGBSplit[0])[3:]
  
  # Confirm image to be labeled is valid
  if os.path.isfile(imageDir + currRGB) and \
    currRGB != '.DS_Store' and \
    currRGBSplit[1] == 'rgb' and \
    currRGBSplit[2] == 'res' and \
    int(currPicNum) >= picRange[0] and \
    int(currPicNum) <= picRange[1]:
    print 'Now labeling', currRGB
    image = mpimg.imread(imageDir + currRGB)
    plt.imshow(image) # Show image
    plt.draw()
    plt.pause(1)
    raw_input()
    plt.close()

    # Make sure label is valid (0,1, or 'u')
    validLabel = False
    while not validLabel:
      label = raw_input('Enter the image label: ')
      print label
      if label != str(0) and label != str(1) and label != 'u':
        print 'Invalid label', label, ', try again'
      else:
        print currRGB, 'was labeled as', label
        validLabel = True

    # Find corresponding depth and ir image for labeling
    depthIm = currRGB.replace('rgb', 'd')
    irIm = currRGB.replace('rgb', 'ir')
    newRGB = currRGB.replace('res', label)
    newDepth = newRGB.replace('rgb', 'd')
    newIr = newRGB.replace('rgb', 'ir')
    os.rename(imageDir + currRGB, imageDir + newRGB)
    os.rename(imageDir + depthIm, imageDir + newDepth)
    os.rename(imageDir + irIm, imageDir + newIr)

print 'Done'
