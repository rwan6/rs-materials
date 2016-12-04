#! /usr/bin/python

import matplotlib.pyplot as plt
import matplotlib.image as mimg
import numpy as np

from sklearn import datasets, svm, metrics
from sklearn.model_selection import train_test_split

# read all the tiled images in
import glob
# test = mimg.imread("/home/rprabala/Downloads/pic_2.bmp")
folder_name = '../rs-materials/rs_resize_pics/tiled/*.bmp'
images1_list = []
labels1_list = []
images0_list = []
labels0_list = []
for filename in glob.glob(folder_name):
  if "rgb" not in filename:
    continue
  cur_rgb_image = plt.imread(filename)
  vals = filename.split("_")
  cur_label = vals[4]
  depth = filename.replace("rgb", "d")
  cur_depth_image = plt.imread(depth)
  concat = np.append(cur_rgb_image, cur_depth_image)

  if cur_label == 0:
  	images0_list.append(concat)
  	labels0_list.append(cur_label)
  else:
  	images1_list.append(concat)
  	labels1_list.append(cur_label)

feat0Array = np.array(images0_list)
labels0Array = np.array(labels0_list)

feat1Array = np.array(images1_list)
labels1Array = np.array(labels1_list)

numSamples = len(images0_list) + len(images1_list)

X0train, X0test, y0train, y0test = train_test_split(
  feat0Array, labels0Array, test_size=0.10, random_state=1)

X1train, X1test, y1train, y1test = train_test_split(
  feat1Array, labels1Array, test_size=0.10, random_state=1)

print("Now training classifier")

# Create a classifier: a support vector classifier
classifier = svm.SVC(gamma=0.001)

classifier.fit(np.append(X0train, X1train), np.append(y0train, y1train))

print("Now predicting with classifier")

expected = np.append(y0test, y1_test)
predicted = classifier.predict(np.append(X0test, X1test))

print("Classification report for classifier %s:\n%s\n"
     % (classifier, metrics.classification_report(expected, predicted)))
print("Confusion matrix:\n%s" % metrics.confusion_matrix(expected, predicted))

