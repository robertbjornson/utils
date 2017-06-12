'''
This script checks a samplesheet to find lanes with barcodes
too close to allow for 1 mismatch.
'''

import sys, operator

def hamming(args):
    bc1, bc2 = args
    id1, bcs1 = bc1
    id2, bcs2 = bc2
    assert len(bcs1)==len(bcs2)
    sum=0
    for a, b in zip(bcs1, bcs2):
        if a!=b:
            sum+=1
    return sum

def test_illegal(s):
    illegal_chars="? ( ) [ ] / \ : ; \" ' , * ^ | & . #".split() + [" "]
    return reduce(operator.__or__, [c in illegal_chars for c in s])

def readSampleSheet(ss):
    bcsByLane={}
    fp=open(ss)
    # skip header
    fp.readline()
    for l in fp:
        fc,lane,sample,ref,bc,desc,control,recipe,operator,project=l.rstrip().split(',')
        if test_illegal(sample) or test_illegal(project):
            print >>sys.stderr, "ERROR: illegal character in line: %s" % l
            sys.exit(-1)
        if bc in bcsByLane.setdefault(lane, []):
            print >> sys.stderr, "ERROR Lane %s had barcode %s listed multiple times.  Please investigate." % (lane, bc)
            sys.exit(-1)
        else:
            bcsByLane.setdefault(lane,[]).append(bc)
    return bcsByLane

def compareBCs(bcs):
    k=len(bcs)
    for i in range(k-1):
        for j in range(i+1, k):
            dist=hamming((("1", bcs[i]), ("2", bcs[j])))
            #print i, j, dist
            if dist < 3:
                print "Conflict %s %s" % (bcs[i], bcs[j])

if __name__=='__main__':
    ss=readSampleSheet(sys.argv[1])
    for ln, bcs in ss.items():
        print "LANE", ln
        compareBCs(bcs)


