#! /usr/bin/python

import os
import sys
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from PIL import Image
from scipy.misc import imsave

inputDir = '../rs-materials/rs_lr_pics/'
outputDir = '../rs-materials/rs_resize_pics/'
desDim = (600, 400)
confirmDim = (400, 600, 3)

for currIm in os.listdir(inputDir):
  if os.path.isfile(inputDir + currIm) and currIm != '.DS_Store':
    image = Image.open(inputDir + currIm)
    image = image.resize(desDim, Image.ANTIALIAS)
    nameSplit = currIm.split('.')
    newName = nameSplit[0] + '_res.bmp'
    image.save(outputDir + newName, 'bmp')
    confIm = mpimg.imread(outputDir + newName)
    if (confIm.shape != confirmDim):
      print currIm, 'was not successfully reshaped! Now exiting'
      sys.exit(1)
    else:
      print 'Successfully reshaped', currIm

print 'Done'