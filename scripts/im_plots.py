#! /usr/bin/python

# Program to plot results of image_classification.py

import os
import sys
import glob
import matplotlib
import operator
import matplotlib.pyplot as plt
import numpy as np

resDir = "../rs-materials/scripts/results_sr/"
# Key: type, Value: [0:p, 0:r, 0:f1, 1:p, 1:r, 1:f1]
resMap = {}

for resFile in glob.glob(resDir + 'crossvalid*.txt'):
  filename = resFile.split('/')
  # Get pic number
  fileReplace = filename[-1].replace('.', '_')
  fileSplit = fileReplace.split('_')
  pic = fileSplit[0]
  types = ' '.join(fileSplit[1:-1])
  
  currFile = open(resFile, 'r')
  currFileLines = currFile.readlines()
  zeroData = currFileLines[2].split()
  oneData = currFileLines[3].split()
      
  # Take entries 2,3,4 for prec, rec, and r1, respectively
  zeroData = zeroData[1:4]
  oneData = oneData[1:4]
  mapData = []
  for i in range(len(zeroData)):
    mapData.append(float(zeroData[i]))
    mapData.append(float(oneData[i]))

  resMap[types] = mapData
  currFile.close()


ind = np.arange(2)
width = 0.25
font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 16}

matplotlib.rc('font', **font)

for k in resMap.keys():
  fig, ax = plt.subplots()
  rects1 = ax.bar(ind, (resMap[k])[0:2], width, color='r')
  rects2 = ax.bar(ind+width, (resMap[k])[2:4], width, color='b')
  rects3 = ax.bar(ind+2*width, (resMap[k])[4:6], width, color='g')

  ax.set_xlabel('Label')
  ax.set_ylabel('Percentage')
  ax.set_xticks(ind + width*1.5)
  ax.set_xticklabels(('Not-Skin', 'Skin'))
  ax.set_title('Precision, Recall, and F1-Score for Type: ' + k)
  ax.legend((rects1[0], rects2[0], rects3[0]), \
    ('Precision', 'Recall', 'F1-Score'), prop={'size':12}, loc=4)

  outfile = resDir + k.replace(' ', '_') + '_results.jpg'
  fig.savefig(outfile)
