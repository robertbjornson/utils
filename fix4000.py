#!/ysm-gpfs/home/lsprog/rdb9/Installed_Ruddle/anaconda2/bin/python

'''
This script addresses a problem with bcl2fastq+twistd+chrom version 68, where the gzip file has an extra field that
seems to confuse chrome.  Workaround is to recompress it.  We also create an md5 sum of the new file.
'''

#SBATCH -c 20
#SBATCH --mail-type=all

import gzip, os, subprocess

from multiprocessing import Pool

def doIt(cmd):
    return subprocess.call(cmd, shell=True)

pool = Pool(processes=int(os.getenv("SLURM_CPUS_PER_TASK")))

cmds=[]

for d, dirs, files in os.walk('.'):
    for f in files:
        if f.endswith("fastq.gz"):
            tmpf=f+".tmp"
            cmd="zcat %(d)s/%(f)s | gzip --fast -c > %(d)s/%(tmpf)s && \
            mv %(d)s/%(f)s %(d)s/%(f)s.bak && mv %(d)s/%(f)s.tmp %(d)s/%(f)s && md5sum %(d)s/%(f)s > %(d)s/%(f)s.md5 && rm %(d)s/%(f)s.bak " % locals()
            cmds.append(cmd)

rets=pool.map(doIt, cmds)

for r in rets:
    print(r)
