
import os, sys

top=sys.argv[1]
max=int(sys.argv[2])

cnts={}

for d, dirs, files in os.walk(top):
    for f in files:
        i=f.find(".")
        if i ==-1: i=0
        suf=f[i:]
        rec=cnts.setdefault(suf, [0,0])
        fn=d+'/'+f
        if os.path.islink(fn):
            sz=0
        else:
            sz=os.path.getsize(d+'/'+f)
        rec[0]+=1; rec[1]+=float(sz)/(1024**4)

recs=sorted([(cnts[k][1], cnts[k][0], k) for k in cnts], reverse=True)
total=sum([rec[0] for rec in recs])
print ("Total %.3f" % total)

for sz, cnt, suf in sorted([(cnts[k][1], cnts[k][0], k) for k in cnts], reverse=True)[:max]:
    print ("%s\t%d\t%.3f" % (suf, cnt, sz))
