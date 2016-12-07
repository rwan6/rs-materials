#! /usr/bin/python

import os
import cv2
from shutil import copyfile

inputDir = '../rs_resize_pics/tiled/'
outputDir = '../rs_resize_pics/tiledeq/'

if not os.path.exists(outputDir):
  os.makedirs(outputDir)

for currIm in os.listdir(inputDir):
  if currIm.endswith('.bmp'):
    if 'rgb' in currIm:
        image = cv2.imread(inputDir + currIm)
        image_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        image_yuv[:,:,0] = cv2.equalizeHist(image_yuv[:,:,0])
        image_output = cv2.cvtColor(image_yuv, cv2.COLOR_YUV2BGR)
        cv2.imwrite(outputDir + currIm, image_output)
    else:
        copyfile(inputDir + currIm, outputDir + currIm)

print 'Done'
