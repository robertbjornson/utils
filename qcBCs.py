
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

import SSparser

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

def seqReader(lane, bcs, start_cycles, cycles, isDual, tilepat, tile, basecalls, compressed):

    funclist=[]

    if isDual[lane]:
        idxs=(0,1)
    else:
        idxs=(0,)
    for idx in idxs:
        for c in range(start_cycles[idx], start_cycles[idx]+cycles[idx]):
            if not compressed:
                #fp=open('%s/L00%s/C%d.1/s_%s_%s.bcl'%(basecalls, lane, c, lane), 'rb')
                fp=open(tilepat% locals())
            else:
                fp=gzip.open('%s/L00%s/C%d.1/s_%s_%s.bcl.gz'%(basecalls, lane, c, lane, tile), 'rb')
            fp.read(4) # skip count
            funclist.append(genFunc(lane, fp))
        if idx < len(idxs)-1:
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
    parser.add_argument("--tilepat", dest="tilepat", default="%(basecalls)s/L00%(lane)s/C%(c)d.1/s_%(lane)s_%(tile)s.bcl", help="Tile to use, default %(default)s")
    parser.add_argument("-m", "--maxtags", dest="maxtags", default=None, type=int, help="maximum tags to report, default %(default)s")
    parser.add_argument("-l", "--lanes", dest="lanes", default='12345678', type=str, help="lanes to check, default %(default)s")
    parser.add_argument("--numreads", dest="numreads", default=100000, type=int, help="maximum # reads to consult, default %(default)s")
    parser.add_argument("-b", "--basecalls", dest="basecalls", default=".", type=str, help="basecalls dir, default %(default)s")
    parser.add_argument("--notcompressed", action="store_false", dest="compressed", default=True, help="compressed bcl files")
    parser.add_argument("--notiem", action="store_false", dest="iem", default=True, help="Sample Sheet in IEM format (HS4000)")
    
    options=parser.parse_args()

    print "Options:" + str(options)

    if options.ss:
        if options.iem:
            bcs, isDual, mindist, samplesPerLane, ok=SSparser.readSampleSheetHS4000(options.ss)
        else:
            bcs, ok=SSparser.readSampleSheet(options.ss)
    else:
        bcs={}
    
    start_cycles=[int(e) for e in options.start_cycles_str.split(',')]
    num_cycles=[int(e) for e in options.num_cycles_str.split(',')]

    print "Summary"
    print "OK? %s" % ok
    print "Hamming Distances:"
    for lane in options.lanes:
        print "%s\t%d" % (lane, mindist[lane])
    print

    for lane in options.lanes:
        expected_found=expected_notfound=found_expected=found_notexpected = 0
        tags={}
        total=0

        for tag in seqReader(lane, bcs[lane], start_cycles, num_cycles, isDual, options.tilepat, options.tile, options.basecalls, options.compressed):
            total+=1
            if tag not in tags:
                tags[tag]=1
            else:
                tags[tag]+=1
            if total >= options.numreads: break
            
        if options.maxtags:
            report=options.maxtags
        else:
            report=int(samplesPerLane[lane]*1.5)
        sortedtags=sorted([[cnt, tag]  for tag, cnt in tags.iteritems()], reverse=True)[:report]
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
