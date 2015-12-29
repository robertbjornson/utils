
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

import os, sys, argparse, struct, operator, textwrap, gzip

def test_illegal(s):
    illegal_chars="? ( ) [ ] / \ : ; \" ' , * ^ | & . #".split() + [" "]
    return reduce(operator.__or__, [c in illegal_chars for c in s])

def readSampleSheetHS4000(ss):
    bcsByLane={}
    hdrdict={}
    fp=open(ss)
    # skip headers
    l=fp.readline()
    while not l.startswith('[Data]'):
        l=fp.readline()
    hdrs=fp.readline().strip().split(',')
    for i, hdr in enumerate(hdrs):
        hdrdict[hdr.lower()]=i

    isdual='index2' in hdrdict    

    for l in fp:
        vals=l.strip().split(',')
        if isdual:
            bc=vals[hdrdict['index']]+'-'+vals[hdrdict['index2']]
        else:
            bc=vals[hdrdict['index']]

        lane=vals[hdrdict['lane']]

        if bc in bcsByLane.setdefault(lane, []):
            print >> sys.stderr, "ERROR Lane %s had barcode %s listed multiple times.  Please investigate." % (lane, bc)
            sys.exit(-1)
        else:
            bcsByLane.setdefault(lane,[]).append(bc)
    return bcsByLane

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

def genFunc(lane, fp):
    def doit():
        c=fp.read(4)
        if len(c)!=4:
            raise Exception("Lane %s had fewer reads (%d) than required (%s) for this analysis.  Please investigate." % (lane, (fp.tell()-4)/4, options.numreads))
        word=struct.unpack('I', c)[0]
        qual=(word & 0xfc) >> 2
        if qual==0:
            base='N'
        else:
            base='ACGT'[word & 0x3]
        return base
    return doit

def seqReader(lane, start_cycles, cycles, tile, basecalls, compressed):

    funclist=[]

    for idx in range(len(start_cycles)):
        for c in range(start_cycles[idx], start_cycles[idx]+cycles[idx]):
            if not compressed:
                fp=open('%s/L00%s/C%d.1/s_%s_%s.bcl'%(basecalls, lane, c, lane, tile), 'rb')
            else:
                fp=gzip.open('%s/L00%s/C%d.1/s_%s_%s.bcl.gz'%(basecalls, lane, c, lane, tile), 'rb')
            fp.read(4) # skip count
            funclist.append(genFunc(lane, fp))
        if idx < len(start_cycles)-1:
            funclist.append(lambda : '-')

    while True:
        yield "".join([f() for f in funclist])
        
epilog='''

The -s, -c, and -n options are required!
-c specifies the first cycle of the index read.  -n gives the length of the barcode. 

For example, for a 76,7,76 run, (where the barcode is actually 6 bases), 
you would specify -n 77 -c 6

Dual barcodes are specified with commas:
-c 77,84, -n 6,6

This program compares an Illumina cavasa 1.8 format samplesheet against
the bcl files in a run.  It flags expected barcodes not found in the data,
as well as barcodes found in the data but not expected.
 
samplespreadsheet is the csv input to demultiplex.pl, looking like:

FCID,Lane,SampleID,SampleReference,Index,Description,Control,Recipe,Operator
FCC03GR,1,JZ05u,Surprise,CAGATC,desc1,N,R1,Vanessa
FCC03GR,1,JZd05,Surprise,CTTGTA,desc1,N,R1,Vanessa

maxtags determines how many observed sample barcodes to report on (the most common)  This
should be the maximum number of barcodes in any lane in the sample sheet, or slightly larger.

tile is the file to use; I usually use 1101.

Run the script in the BaseCalls directory.

You will get an output set for each lane, describing what barcodes were expected, followed by the barcdes seen.
Barcodes seen that weren\'t expected are marked with *.

Example:
python ~/utils/qcBCs.py -s samplesheet.csv -c 77 -n 6 > barcodereport.txt

'''

if __name__=='__main__':

    print "Invocation: " + " ".join(sys.argv)
    print "Cwd: " + os.getcwd()

    parser=argparse.ArgumentParser(epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-s", "--samplesheet", dest="ss", required=True, help="samplesheet file")
    parser.add_argument("-c", "--startcycle", dest="start_cycles_str", required=True, type=str, help="first barcode cycles")
    parser.add_argument("-n", "--numcycles", dest="num_cycles_str", type=str, required=True, help="number of barcode cycles")
    parser.add_argument("-t", "--tile", dest="tile", default="1101", help="Tile to use, default %(default)s")
    parser.add_argument("-m", "--maxtags", dest="maxtags", default=10, type=int, help="maximum tags to report, default %(default)s")
    parser.add_argument("-l", "--lanes", dest="lanes", default='12345678', type=str, help="lanes to check, default %(default)s")
    parser.add_argument("--numreads", dest="numreads", default=100000, type=int, help="maximum # reads to consult, default %(default)s")
    parser.add_argument("-b", "--basecalls", dest="basecalls", default=".", type=str, help="basecalls dir, default %(default)s")
    parser.add_argument("-z", "--compressed", action="store_true", dest="compressed", default=False, help="compressed bcl files")
    parser.add_argument("--iem", action="store_true", dest="iem", default=False, help="Sample Sheet in IEM format (HS4000)")
    
    options=parser.parse_args()

    print "Options:" + str(options)

    if options.ss:
        if options.iem:
            bcs=readSampleSheetHS4000(options.ss)
        else:
            bcs=readSampleSheet(options.ss)
    else:
        bcs={}

    maxSamplePerLane = max([len(v) for v in bcs.itervalues()])
    if maxSamplePerLane>=options.maxtags*.75:
        print >>sys.stderr, "WARNING: Lane seen with %d samples.  Consider increasing maxtags (-m)" % maxSamplePerLane
    start_cycles=[int(e) for e in options.start_cycles_str.split(',')]
    num_cycles=[int(e) for e in options.num_cycles_str.split(',')]

    for lane in options.lanes:
        expected_found=expected_notfound=found_expected=found_notexpected = 0
        tags={}
        total=0

        for tag in seqReader(lane, start_cycles, num_cycles, options.tile, options.basecalls, options.compressed):
            total+=1
            if tag not in tags:
                tags[tag]=1
            else:
                tags[tag]+=1
            if total >= options.numreads: break
            
        sortedtags=sorted([[cnt, tag]  for tag, cnt in tags.iteritems()], reverse=True)[:options.maxtags]
        foundtags=[tag for cnt,tag in sortedtags]
        print "Lane %s" % lane
        if lane in bcs:
            print "Expected ",
            for tag in bcs[lane]:
                if tag in foundtags:
                    tmp=""
                    expected_found+=1
                else:
                    tmp="*"
                    expected_notfound+=1
                print "%s%s" % (tag, tmp),
            print

        print "Summary found %d not found %d" % (expected_found, expected_notfound)
        print "Found"
        print "\tBarcode\t\tCnt\t%"
        
        for cnt, tag in sortedtags:
            if lane in bcs and tag not in bcs[lane]:
                tmp="*"
                found_notexpected+=1
            else:
                tmp=" "
                found_expected+=1
            print "\t%s%s" % (tag, tmp),
            print "\t%d\t%f" % (cnt, float(cnt)/total)

        print "Summary expected %d not expected %d" % (found_expected, found_notexpected)
