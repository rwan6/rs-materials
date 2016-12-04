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
images_list = []
labels_list = []
for filename in glob.glob(folder_name):
  if "rgb" not in filename:
    continue
  cur_rgb_image = plt.imread(filename)
  vals = filename.split("_")
  cur_label = vals[4]
  depth = filename.replace("rgb", "d")
  cur_depth_image = plt.imread(depth)
  concat = np.append(cur_rgb_image, cur_depth_image)

  images_list.append(concat)
  labels_list.append(cur_label)

featArray = np.array(images_list)
labelsArray = np.array(labels_list)
numSamples = len(images_list)

Xtrain, Xtest, ytrain, ytest = train_test_split(
  featArray, labelsArray, test_size=0.10, random_state=1)

print("Now training classifier")

# Create a classifier: a support vector classifier
classifier = svm.SVC(gamma=0.001)

classifier.fit(Xtrain, ytrain)

print("Now predicting with classifier")

expected = ytest
predicted = classifier.predict(Xtest)

print("Classification report for classifier %s:\n%s\n"
     % (classifier, metrics.classification_report(expected, predicted)))
print("Confusion matrix:\n%s" % metrics.confusion_matrix(expected, predicted))

