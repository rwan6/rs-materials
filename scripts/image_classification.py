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
#folder_name = '../rs_res_sr_pics/tiled/*.bmp'
folder_name = '../rs_resize_pics/tiled/*.bmp'
def main(classif, test0_size, test1_size):
  # Read in tiled images
  images1_list = []
  labels1_list = []
  images0_list = []
  labels0_list = []

  images1_map = {}
  images0_map = {}

  type_list = []
  types = args.type.split("_")
  if "rgb" in types:
    type_list.append("rgb")
  if "d" in types:
    type_list.append("d")
  if "ir" in types:
    type_list.append("ir")
  
  for filename in sorted(glob.glob(folder_name)):
    #if "rgb" not in filename:
    #    continue
    if type_list[0] not in filename:
        continue
    vals = filename.split("/")
    image_name = vals[len(vals) - 1]
    tokens = image_name.split("_")
    cur_label = tokens[2]
    cur_key = "_".join((tokens[0], tokens[3], tokens[4]))
    cur_type = tokens[1]


    # If we don't want this particular input, continue
    #if cur_type not in types:
    #	continue

    # If this is not labeled, or unknown label, continue
    if cur_label == "res" or cur_label == "u":
    	continue
    cur_image = plt.imread(filename)
    cur_np_arr = np.ndarray.flatten(cur_image)
    #cur_np_arr = np.append(cur_image, cur_d_image)
    for i in range(1,len(type_list)):
        #print filename.replace(type_list[0], type_list[i])
        cur_np_arr = np.append(cur_np_arr, plt.imread(filename.replace(type_list[0], type_list[i])))

    if cur_label == '0':
        images0_list.append(cur_np_arr)
        labels0_list.append(cur_label)
    else:
        images1_list.append(cur_np_arr)
        labels1_list.append(cur_label)


  



  #images0_list = images0_map.values()
  #images1_list = images1_map.values()
  #labels0_list = np.zeros(len(images0_list))
  #labels1_list = np.ones(len(images1_list))

  feat0Array = np.array(images0_list)
  labels0Array = np.array(labels0_list)

  feat1Array = np.array(images1_list)
  labels1Array = np.array(labels1_list)

  numSamples = len(images0_list) + len(images1_list)

  X0train, X0test, y0train, y0test = train_test_split(
    feat0Array, labels0Array, test_size=test0_size, random_state=1234)

  X1train, X1test, y1train, y1test = train_test_split(
    feat1Array, labels1Array, test_size=test1_size, random_state=1234)

  print 'label0 total size:', labels0Array.shape
  print 'label0train size:', y0train.shape
  print 'label1 total size:', labels1Array.shape
  print 'label1train size:', y1train.shape
  print 'Now training classifier'

  # Create a classifier: a support vector classifier
  if classif == 'svm':
    classifier = svm.LinearSVC(C=1.5)
  elif classif == 'lr':
    #classifier = linear_model.LogisticRegression(solver='lbfgs')
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
  ap.add_argument('--type', default="rgb",
  				  help='All types of data to be included, separated by a _')

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

