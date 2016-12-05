#! /usr/bin/python

import sys
import argparse
import glob
import matplotlib.pyplot as plt
import matplotlib.image as mimg
import numpy as np
from sklearn import datasets, svm, metrics, linear_model, ensemble
from sklearn.model_selection import train_test_split

# test = mimg.imread("/home/rprabala/Downloads/pic_2.bmp")
folder_name = '../rs-materials/rs_resize_pics/tiled/*.bmp'

def main(classif, test0_size, test1_size):
  # Read in tiled images
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

    if cur_label == '0':
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
    feat0Array, labels0Array, test_size=test0_size)

  X1train, X1test, y1train, y1test = train_test_split(
    feat1Array, labels1Array, test_size=test1_size)

  print 'label0 total size:', labels0Array.shape
  print 'label0train size:', y0train.shape
  print 'label1 total size:', labels1Array.shape
  print 'label1train size:', y1train.shape
  print 'Now training classifier'

  # Create a classifier: a support vector classifier
  if classif == 'svm':
    classifier = svm.LinearSVC(C=1.5)
  elif classif == 'lr':
    # classifier = linear_model.LogisticRegression(solver='lbfgs')
    classifier = linear_model.LogisticRegression()
  else: # Must be rfc
    classifier = ensemble.RandomForestClassifier()

  classifier.fit(np.concatenate((X0train, X1train)), \
    np.concatenate((y0train, y1train)))

  print 'Now predicting with classifier'
  expected = np.concatenate((y0test, y1test))
  predicted = classifier.predict(np.concatenate((X0test, X1test)))

  print 'Classification report for classifier %s:\n%s\n' \
       % (classifier, metrics.classification_report(expected, predicted))
  print 'Confusion matrix:\n%s' % metrics.confusion_matrix(expected, predicted)

if __name__ == '__main__':
  ap = argparse.ArgumentParser()
  ap.add_argument('--c', default='svm',
                  help='Classifier options: svm, lr, rfc. Default is svm.')
  ap.add_argument('--t0', type=float, default=0.80,
                  help='Test0 size. Default is 0.80.')
  ap.add_argument('--t1', type=float, default=0.20,
                  help='Test1 size. Default is 0.20.')
  args = ap.parse_args()
  
  # Simple error checking
  if args.t0 < 0 or args.t0 > 1.0:
    print "t0 must be between 0 and 1.0, inclusive"
    sys.exit(1)
  if args.t1 < 0 or args.t1 > 1.0:
    print "t1 must be between 0 and 1.0, inclusive"
    sys.exit(1)
  if args.c != 'svm' and args.c != 'lr' and args.c != 'rfc':
    print 'Classifier options: svm, lr, rfc'
    sys.exit(1)

  main(args.c, args.t0, args.t1)

