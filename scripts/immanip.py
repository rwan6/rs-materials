#! /usr/bin/python

# Program to resize images

import os
import sys
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from PIL import Image
from scipy.misc import imsave

# Directories and image dimensions
inputDir = '../rs-materials/rs_sr_pics/'
outputDir = '../rs-materials/rs_res_sr_pics/'
desDim = (600, 400)
confirmDim = (400, 600, 3)

# Iterate through all images and resize
for currIm in os.listdir(inputDir):
  if os.path.isfile(inputDir + currIm) and currIm != '.DS_Store':
    image = Image.open(inputDir + currIm)
    image = image.resize(desDim, Image.ANTIALIAS)
    nameSplit = currIm.split('.')
    newName = nameSplit[0] + '_res.bmp'
    image.save(outputDir + newName, 'bmp')
    confIm = mpimg.imread(outputDir + newName)
    
    # Confirm reshaping was successful
    if (confIm.shape != confirmDim):
      print currIm, 'was not successfully reshaped! Now exiting'
      sys.exit(1)
    else:
      print 'Successfully reshaped', currIm

print 'Done'
