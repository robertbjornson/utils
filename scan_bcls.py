

import glob, os, struct


tiles=["%d%02d" % (a, b) for a in [11, 12, 21, 22] for b in range(1, 17)]
lanes=range(1,3)
cycles=range(1, 133)

print "checking stats files"
for l in lanes:
    for c in cycles:
        for t in tiles:
            f="L00%s/C%s.1/s_%s_%s.stats" % (l, c, l, t)
            if os.path.getsize(f) != 112:
                print "bad stats file %s size %d" % (f, os.path.getsize(f))
                continue
            fp=open(f, 'rb')
            cycl=struct.unpack("I", fp.read(4))[0]
            fp.close()
            if cycl != c-1:
                print "FIRST INT %s: expect %d got %d" % (f, c-1, cycl)


print "checking bcl files"

for l in lanes:
    print "setting expectations for L00%s" % l
    expect={}
    for t in tiles:
        f="L00%s/C77.1/s_%s_%s.bcl" % (l, l, t)
        if not os.path.isfile(f):
            print "FILE %s missing" %f
            continue
        size=os.path.getsize(f)
        k=os.path.basename(f)
        expect[k]=size
    
    print "checking bcls for %s" % l
    for c in cycles:
        for t in tiles:
            f="L00%s/C%s.1/s_%s_%s.bcl" % (l, c, l, t)
            if not os.path.isfile(f):
                print "FILE %s missing" %f
                continue

            k=os.path.basename(f)
            sz=os.path.getsize(f)
            if sz!=expect[k]:
                print "FILESIZE %s: expect %d got %d" % (f, expect[k], sz)
                continue

            fp=open(f, 'rb')
            cnt=struct.unpack("I", fp.read(4))[0]
            fp.close()
            if cnt != expect[k]-4:
                print "FIRST INT %s: expect %d got %d" % (f, expect[k]-4, cnt)

    
