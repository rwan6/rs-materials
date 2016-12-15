#! /usr/bin/python

# Script to take in images, decompose into features, classify using selected
# supervised learning classifier, and display heatmap and classification
# statistics.

import sys
import argparse
import glob
import os
import matplotlib.pyplot as plt
import matplotlib.image as mimg
import numpy as np
import matplotlib.ticker as plticker
from sklearn import datasets, svm, metrics, linear_model, ensemble
from sklearn.model_selection import train_test_split
try:
  from PIL import Image
except ImportError:
  import Image

# Directories
subfolder = "tiled"
resultsDir = "../rs-materials/scripts/results_sr/"
folder = '../rs-materials/rs_res_sr_pics/'
folder_name = os.path.join(folder, subfolder, "*.bmp")

# Results lists
images1_list = []
labels1_list = []
images0_list = []
labels0_list = []

images1_map = {}
images0_map = {}

heatmap0_list = []
heatmap1_list = []

file_tracker_list = []

# Function to draw heatmap on top of raw image
def draw_heatmap(pics, file_tracker_list, expected, predicted, hm, save, types):
    incorrect_files = []
    skin_files = []
    true_skin_files = []
    for i in range(0, len(expected)):
	   if expected[i] != predicted[i]:
	     incorrect_files.append(file_tracker_list[i])
    for i in range(0, len(predicted)):
      if predicted[i] == "1":
    		skin_files.append(file_tracker_list[i])
      if expected[i] == "1":
        true_skin_files.append(file_tracker_list[i])

	pic_strings = ["pic" + s for s in pics]
	my_dpi = 200
	orig_filename = os.path.join(folder, pic_strings[0]+ "_rgb_res.bmp")
    image = Image.open(orig_filename)
    fig=plt.figure(figsize=(float(image.size[0])/my_dpi,float(image.size[1])/my_dpi),dpi=my_dpi)
    ax=fig.add_subplot(111)

    # Remove whitespace from around the image
    fig.subplots_adjust(left=0,right=1,bottom=0,top=1)

    yInterval = 40.
    xInterval = 60.
    yloc = plticker.MultipleLocator(base=xInterval)
    xloc = plticker.MultipleLocator(base=yInterval)

    ax.xaxis.set_major_locator(yloc)
    ax.yaxis.set_major_locator(xloc)

    ax.grid(which='major', axis='both', linestyle='-')

    ax.imshow(image)

    nx=abs(int(float(ax.get_xlim()[1]-ax.get_xlim()[0])/float(xInterval)))
    ny=abs(int(float(ax.get_ylim()[1]-ax.get_ylim()[0])/float(yInterval)))

    print skin_files

    print nx, ny
    overlay = np.zeros((400, 600,3), dtype=np.uint8)

    # Add some labels to the grid
    for j in range(ny):
        y = yInterval/2.+j*yInterval
        for i in range(nx):
            x = xInterval/2.+float(i)*xInterval
            #ax.text(x,y,'({:d},{:d})'.format(j,i),color='w',ha='center',va='center', size=5)

    for j in range(ny):
    	for i in range(nx):
            files_list = ["_".join((pic_strings[0], s, labelgen, str(j), str(j*10+i))) + ".bmp" for s in ["rgb", "d", "ir"] for labelgen in ["0", "1"]] 
    	    ones_list = [x for x in files_list for g in ["rgb_1_", "d_1_", "ir_1_"] if g in x]
            zeros_list = [x for x in files_list for g in ["rgb_0_", "d_0_", "ir_0_"] if g in x ]

            if hm == 'a':
	            if any(this_file in incorrect_files for this_file in files_list):
	               overlay[j*40:(j+1)*40,i*60:(i+1)*60] = [255,0,0]
	            else:
	                overlay[(j*40):(j+1)*40 - 1, i*60:(i+1)*60 -1] = [0,255,0]
            elif hm == 's':
                if any(x in skin_files for x in ones_list):
   		            overlay[(j*40):(j+1)*40 - 1, i*60:(i+1)*60 -1] = [0,255,0]
                elif any(x in skin_files for x in zeros_list):
   				    overlay[(j*40):(j+1)*40 - 1, i*60:(i+1)*60 -1] = [255,0,0]
                elif any(x in true_skin_files for x in ones_list):
                    overlay[(j*40):(j+1)*40 - 1, i*60:(i+1)*60 -1] = [0,0,255]


    plt.hold(True)
    plt.imshow(overlay, alpha=.2)
    if save:
      outfile = resultsDir + '_'.join((pic_strings[0], '_'.join(types))) + \
       ".jpg"
      fig.savefig(outfile)
    else:
      plt.show()

def heatmap_images(types, pics):
  pic_strings = ["pic" + s for s in pics]

  for filename in sorted(glob.glob(folder_name)):

    vals = filename.split("/")
    image_name = vals[len(vals) - 1]
    tokens = image_name.split("_")
    cur_label = tokens[2]
    cur_key = "_".join((tokens[0], tokens[3], tokens[4]))
    cur_type = tokens[1]
    if types[0] not in image_name:
      continue
    # If this is not labeled, or unknown label, continue
    if cur_label == "res" or cur_label == "u":
      continue

    cur_image = plt.imread(filename)
    cur_np_arr = np.ndarray.flatten(cur_image)
    for i in range(1,len(types)):
      cur_np_arr = np.append(cur_np_arr, \
        plt.imread(os.path.join(folder, subfolder, image_name.replace(types[0], types[i]))))

    if cur_label == '0':
      if tokens[0] in pic_strings:
        heatmap0_list.append(cur_np_arr)
        file_tracker_list.append(image_name)
      else:
        images0_list.append(cur_np_arr)
        labels0_list.append(cur_label)
    else:
      if tokens[0] in pic_strings:
        heatmap1_list.append(cur_np_arr)
        file_tracker_list.append(image_name)
      else:
        images1_list.append(cur_np_arr)
        labels1_list.append(cur_label)

# Collect features for desired types
def process_images(types):
  for filename in sorted(glob.glob(folder_name)):
    if types[0] not in filename:
        continue
    vals = filename.split("/")
    image_name = vals[len(vals) - 1]
    tokens = image_name.split("_")
    cur_label = tokens[2]
    cur_key = "_".join((tokens[0], tokens[3], tokens[4]))
    cur_type = tokens[1]

    # If this is not labeled, or unknown label, continue
    if cur_label == "res" or cur_label == "u":
      continue

    cur_image = plt.imread(filename)
    cur_np_arr = np.ndarray.flatten(cur_image)
    for i in range(1,len(types)):
      cur_np_arr = np.append(cur_np_arr, \
        plt.imread(filename.replace(types[0], types[i])))

    if cur_label == '0':
      images0_list.append(cur_np_arr)
      labels0_list.append(cur_label)
    else:
      images1_list.append(cur_np_arr)
      labels1_list.append(cur_label)

# Tune SVM parameters
def tuneSVM(X0train, X1train, X0test, X1test, y0train, y1train, y0test, y1test):
  losses = ['hinge', 'squared_hinge']
  penalties = ['l1', 'l2']
  duals = [True, False]
  Cs = np.logspace(-2, 2, num=15)

  for l in losses:
    for p in penalties:
      for d in duals:
        for c in Cs:
          classifier = svm.LinearSVC(penalty=p, loss=l, dual=d, C=c)
          classifier.fit(np.concatenate((X0train, X1train)), np.concatenate((y0train, y1train)))
          expected = np.concatenate((y0test, y1test))
          predicted = classifier.predict(np.concatenate((X0test, X1test)))
          print 'Classification report for %s %s %d %f:\n%s\n' % (l, p, d, c, metrics.classification_report(expected, predicted))

def tuneLR(X0train, X1train, X0test, X1test, y0train, y1train, y0test, y1test):
  classifiers = ['newton-cg', 'lbfgs', 'liblinear', 'sag']
  penalties = ['l2']
  multi_classes = ['ovr', 'multinomial']
  Cs = np.logspace(-2, 2, num=15)

  for cf in classifiers:
    for p in penalties:
      for mc in multi_classes:
        for c in Cs:
          if p == 'l1' and cf != 'liblinear':
            continue
          if mc == 'multinomial' and cf == 'liblinear':
            continue

          classifier = linear_model.LogisticRegression(penalty=p, C=c, solver=cf, multi_class=mc, n_jobs=-1)
          classifier.fit(np.concatenate((X0train, X1train)), np.concatenate((y0train, y1train)))
          expected = np.concatenate((y0test, y1test))
          predicted = classifier.predict(np.concatenate((X0test, X1test)))
          print 'Classification report for %s %s %f %s:\n%s\n' % (cf, p, c, mc, metrics.classification_report(expected, predicted))

# Main function that takes in inputted parameters and determines which
# classifier to use, whether a heatmap should be produced, what features to
# use, and whether to save the image and its statistics or display it
def main(classif, test0_size, test1_size, types, svmc, pics, hm, tune, save):
  # Read in tiled images
  if len(pics) == 0:
    process_images(types)
  else:
    heatmap_images(types, pics)

  feat0Array = np.array(images0_list)
  labels0Array = np.array(labels0_list)

  feat1Array = np.array(images1_list)
  labels1Array = np.array(labels1_list)

  numSamples = len(images0_list) + len(images1_list)

  if len(pics) == 0:
    X0train, X0test, y0train, y0test = train_test_split(
      feat0Array, labels0Array, test_size=test0_size) #, random_state=1234)

    X1train, X1test, y1train, y1test = train_test_split(
      feat1Array, labels1Array, test_size=test1_size) #, random_state=1234)

  else:
    X0train = feat0Array
    X1train = feat1Array
    y1train = labels1Array
    y0train = labels0Array

    X1test = np.array(heatmap1_list)
    X0test = np.array(heatmap0_list)
    y0test = ["0" for s in range(0,len(X0test))]
    y1test = ["1" for s in range(0,len(X1test))]

  if len(X0test) == 0 or len(X1test) == 0:
    print 'Test set is all 0 or all 1. Now exiting...'
    sys.exit(0)

  # Create a classifier: a support vector classifier
  if classif == 'svm':
    classifier = svm.LinearSVC(C=svmc)
  elif classif == 'lr':
    classifier = linear_model.LogisticRegression()
  else: # Must be rfc
    classifier = ensemble.RandomForestClassifier(n_estimators=500)

  print 'label0 total size:', labels0Array.shape
  print 'label0train size:', y0train.shape
  print 'label1 total size:', labels1Array.shape
  print 'label1train size:', y1train.shape
  print 'Now training classifier'

  if tune:
    if tune == 'lr':
      tuneLR(X0train, X1train, X0test, X1test, y0train, y1train, y0test, y1test)
    elif tune == 'svm':
      tuneSVM(X0train, X1train, X0test, X1test, y0train, y1train, y0test, y1test)
    return

  classifier.fit(np.concatenate((X0train, X1train)), \
    np.concatenate((y0train, y1train)))

  print 'Now predicting with classifier'
  expected = np.concatenate((y0test, y1test))
  predicted = classifier.predict(np.concatenate((X0test, X1test)))

  print 'Classification report for classifier %s:\n%s\n' \
       % (classifier, metrics.classification_report(expected, predicted))
  print 'Confusion matrix:\n%s' % metrics.confusion_matrix(expected, predicted)

  if len(pics) != 0:
    draw_heatmap(pics, file_tracker_list, expected, predicted, hm, save, types)

  if save:
    if len(pics) != 0:
      pic_strings = ["pic" + s for s in pics]
      outfile = resultsDir + '_'.join((pic_strings[0], '_'.join(types))) + ".txt"
    else:
      outfile = resultsDir + 'crossvalid_' + '_'.join(types) + ".txt"
 
    of = open(outfile,'w')
    # of = open('test.txt', 'w')
    of.write(metrics.classification_report(expected, predicted))
    of.write('\n\n')
    conf_matr = metrics.confusion_matrix(expected, predicted)
    of.write(str(conf_matr))
    of.close()

if __name__ == '__main__':
  ap = argparse.ArgumentParser()
  ap.add_argument('--c', default='rfc',
                  help='Classifier options: svm, lr, rfc. Default is rfc.')
  ap.add_argument('--t0', type=float, default=0.20,
                  help='Test0 size. Default is 0.20.')
  ap.add_argument('--t1', type=float, default=0.20,
                  help='Test1 size. Default is 0.20.')
  ap.add_argument('--type', nargs='+', required=True,
  				  help='All types of data to be included.')
  ap.add_argument('--pic', nargs='+', default="",
                  help='Picture numbers to heatmap')
  ap.add_argument('--svmc', type=float, default=3.0,
  				        help='C-parameter for svm. Default is 3.')
  ap.add_argument('--hm', default="s",
                  help='Type of heatmap: a, s. Default is s.')
  ap.add_argument('--tune', default='',
                    help='Classifier to tune')
  ap.add_argument('--save', type=bool, default=False,
                  help='Save the image/logs. Default is False')

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
  if args.tune not in ['lr', 'svm', 'rfc', '']:
    print 'Unexpected tuning type'
    sys.exit(1)

  main(args.c, args.t0, args.t1, args.type, args.svmc, args.pic, args.hm, \
   args.tune, args.save)

