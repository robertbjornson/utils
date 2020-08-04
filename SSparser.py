
'''
Copyright 2012, Robert Bjornson, Yale University

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''

import sys, operator

def hammingDist(s1, s2):
    dist=0
    assert(len(s1)==len(s2))
    for c1, c2 in zip(s1, s2):
        if c1!=c2: dist+=1
    return dist

def minHammingDist(l):
    mindist=99999
    pair=[]
    n=len(l)
    for i1 in range(0,n-1):
        for i2 in range(i1+1, n):
            hd=hammingDist(l[i1], l[i2])
            if hd <= mindist:
                mindist=hd            
    return mindist

def test_illegal(s):
    legal_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    legal_chars+=legal_chars.lower()
    legal_chars+="01234567890-_"
    illegal_chars=set(s).difference(set(legal_chars))
    return "".join(illegal_chars)


def dashify(bc):
    if len(bc) == 1: return str(bc)
    if not bc[1]: return str(bc[0])
    return '-'.join(bc)
    
'''
barcode output looks like this:
bcsByLane {'6.': [('GGGGGG', None)], '1': [('GGGGGG', None), ('CCGGGG', None), ('TTGGGG', None), ('AAGGGG', None), ('AAGGGG', 'CCCCCC')], '3': [('GGGGGG', None)], '2': [('GGGGGG', 'GGGGGG'), ('CCGGGG', 'CGGGGG'), ('TTGGGG', 'TGGGGG')], '5': [('GGGGGG', None)], '4': [('GGGGGG', None)], '7': [('GGGGGG', None)], '8': [('GGGGGG', None)]}

'''
def readSampleSheetHS4000(ss):
    ok=True
    bcsByLane={}
    hdrdict={}
    fp=open(ss)
    bcsInLane={}
    mindist={}
    
    # skip headers
    l=fp.readline()
    while not l.startswith('[Data]'):
        l=fp.readline()
    hdrs=fp.readline().strip().split(',')
    for i, hdr in enumerate(hdrs):
        hdrdict[hdr.lower()]=i

    isDual={}
    
    for lnum, l in enumerate(fp):
        l=l.strip()
        vals=l.split(',')
        lane=vals[hdrdict['lane']]
        if 'index2' in hdrdict and vals[hdrdict['index2']]:
            bc=(vals[hdrdict['index']],vals[hdrdict['index2']])
            if lane in isDual and isDual[lane]==False:
                print >>sys.stderr, "ERROR: single and dual bcs in lane %s in samplename in line %d: %s" % (str(bad), lnum, l)
                ok=False
            else:
                isDual[lane]=True
        else:
            bc=(vals[hdrdict['index']], None)
            if lane in isDual and isDual[lane]==True:
                print >>sys.stderr, "ERROR: single and dual bcs in lane %s in samplename in line %d: %s" % (str(bad), lnum, l)
                ok=False
            else:
                isDual[lane]=False

        bad=test_illegal(vals[hdrdict['samplename']])
        if bad:
            print >>sys.stderr, "ERROR: illegal character(s) %s in samplename in line %d: %s" % (str(bad), lnum, l)
            ok=False 

        bad=test_illegal(vals[hdrdict['project']])
        if bad:
            print >>sys.stderr, "ERROR: illegal character(s) %s in project in line %d: %s" % (str(bad), lnum, l)
            ok=False 

        if bc in bcsByLane.setdefault(lane, []):
            print >> sys.stderr, "ERROR Lane %s had barcode %s listed multiple times.  Please investigate." % (lane, bc)
            ok=False
        else:
            bcsByLane.setdefault(lane,[]).append(bc)
    # check that all bcs in a lane are consistently 1 or 2 indexes
    for lane,bcs in bcsByLane.iteritems():
        bc1s=[bc[0] for bc in bcs]
        bc2s=[bc[1] for bc in bcs]
        if any(bc2s) and not all(bc2s):
            print >> sys.stderr, "ERROR Lane %s had a mixture of single and dual barcodes.  Please investigate." % (lane,)
            ok=False
        
    maxSamplesPerLane = [len(bcs) for bcs in bcsByLane.values()]
    samplesPerLane = {lane:len(bcs) for (lane, bcs) in bcsByLane.items()}
    # convert bc lists to strings with dashes
    bcsByLane = {lane:[dashify(bc) for bc in bcs] for (lane, bcs) in bcsByLane.items()}            

    for lane,bcs in bcsByLane.iteritems():
        mindist[lane]=minHammingDist(bcs)

    return bcsByLane, isDual, mindist, samplesPerLane, ok

def readSampleSheet(ss):
    ok=True
    bcsByLane={}
    fp=open(ss)
    # skip header
    fp.readline()
    for lnum, l in enumerate(fp):
        fc,lane,sample,ref,bc,desc,control,recipe,operator,project=l.rstrip().split(',')
        if test_illegal(sample) or test_illegal(project):
            print >>sys.stderr, "ERROR: illegal character in line %d: %s" % (lnum, l)
            ok=False 
        if bc in bcsByLane.setdefault(lane, []):
            print >> sys.stderr, "ERROR Lane %s had barcode %s listed multiple times.  Please investigate." % (lane, bc)
            ok=False 
        else:
            bcsByLane.setdefault(lane,[]).append(bc)
    return bcsByLane, ok

if __name__=='__main__':
    bcsByLane, isDual, mindist, maxSamplesPerLane, ok = readSampleSheetHS4000(sys.argv[1])
    print "Status was %s" % ok
    print "bcsByLane %s" % str(bcsByLane)
    print "isDual %s" % str(isDual)
    print "mindist %s" % str(mindist)
    print "maxSamplesPerLane %s" % str(maxSamplesPerLane)
