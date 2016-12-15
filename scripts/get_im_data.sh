#!/bin/bash

# Script to collect realsense image data using image_classification.py

maxPic=1

declare -a typeOptions=(
"rgb"
"d"
"ir"
"rgb d"
"rgb ir"
"ir d"
"rgb d ir"
)

# Counter up to maximum pictures
i="1"

# Gather results by iterating through all types of configurations
while [ $i -le $maxPic ]; do
  for t in "${typeOptions[@]}"; do
    echo "==== Running classification for pic: "${i}" and type(s): "${t}" ===="
    # ./image_classification.py --pic $i --type $t --save True
    ./image_classification.py --type $t --save True
  done
  i=$[$i+1]
done
