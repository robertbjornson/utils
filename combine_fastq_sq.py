
import glob,re,os, sys

pat=re.compile('(Project.+)/(Sample.+)/(.+)_(\d+).fastq.gz')
targets=glob.glob('Project*/Sample*/*001.fastq.gz')

def sort_files(fs):
    l=[]
    for f in fs:
        mo=pat.match(f)
        idx=int(mo.group(4))
        l.append([idx, f])
    l.sort()
    newl=[e[1] for e in sorted(l)]
    return newl

if len(sys.argv) == 2:
    pfx=sys.argv[1]
else:
    pfx="combine"

fp=open("%sjobs.txt"%pfx, "w")

for target in targets:
    srcs=glob.glob(target.replace('001.fastq.gz','*.fastq.gz'))
    srcs=sort_files(srcs)
    mo=pat.match(target)
    dest='%s/%s/%s_all.fastq' % mo.groups()[0:3]
    sumf='%s/%s/%s_all.md5sum' % mo.groups()[0:3]
    
    print >> fp, "cd %s; zcat %s | tee %s | md5sum > %s; chmod a+r %s" % (os.getcwd(), " ".join(srcs), dest, sumf, dest)

fp.close()

os.system("module load SimpleQueue; sqCreateScript -n 10 %sjobs.txt > %s.sh" %(pfx, pfx) )
