/ycga-gpfs/apps/hpc/software/bcl2fastq2/v2.19.0/bin/bcl2fastq -R ../../../
--output-dir QC -p 20 --sample-sheet emptySS.csv \
--tiles 120[0-9] --create-fastq-for-index-reads \
> QC.log 2> QC.err 
