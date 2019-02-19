#!/bin/bash

#SBATCH -c 16

module load parallel

parallel -j ${SLURM_CPUS_PER_TASK} --plus "echo {}; md5sum {} > {/fastq.gz/md5sum.new}" ::: $(find . -name "*.fastq.gz" -print)
