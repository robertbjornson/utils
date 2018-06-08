#!/bin/bash

# to create sum files for all fastq's 
# cd to the Unaligned dir(s) and run this script 
set -x

for f in $(find . -name "*.fastq.gz" -print)
do
  mdfile=${f/fastq.gz/md5sum}
  md5sum $f > $mdfile
done

