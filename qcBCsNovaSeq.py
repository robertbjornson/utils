
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
import fastq

def test_illegal(s):
    illegal_chars="? ( ) [ ] / \ : ; \" ' , * ^ | & . #".split() + [" "]
    return reduce(operator.__or__, [c in illegal_chars for c in s])

def readSampleSheetNovaSeq(ss):
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


def novaSeqReader(lane, basecalls, num_cycles):
    r1 = fastq.fastqReader('%s/Undetermined_S0_L00%s_I1_001.fastq.gz' % (basecalls, lane))
    if len(num_cycles)==2:
        r2 = fastq.fastqReader('%s/Undetermined_S0_L00%s_I2_001.fastq.gz' % (basecalls, lane))

    while True:
        i1 = r1.next()[1][:num_cycles[0]]
        if len(num_cycles)==2:
            i2 = r2.next()[1][:num_cycles[1]]
            yield i1+'-'+i2
        else:
            yield i1


epilog='''

The -s option is required!

This program compares an Illumina Novaseq format samplesheet against
the index fastqs. Those can be created by running bcl2fastq2 with an empty samplesheet
--create-fastq-for-index-reads, and a subset of the tiles, e.g.
--tiles s_[1-2]_120[0-9]

This program flags expected barcodes not found in the data,
as well as barcodes found in the data but not expected.
 
maxtags determines how many observed sample barcodes to report on (the most common)  This
should be the maximum number of barcodes in any lane in the sample sheet, or slightly larger.

Run the script in the s directory.

You will get an output set for each lane, describing what barcodes were expected, followed by the barcdes seen.
Barcodes seen that weren\'t expected are marked with *.

Example:
python ~/utils/qcBCsNovaSeq.py -s samplesheet.csv > barcodereport.txt

'''

if __name__=='__main__':

    print "Invocation: " + " ".join(sys.argv)
    print "Cwd: " + os.getcwd()

    parser=argparse.ArgumentParser(epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-s", "--samplesheet", dest="ss", required=True, help="samplesheet file")
    parser.add_argument("-m", "--maxtags", dest="maxtags", default=10, type=int, help="maximum tags to report, default %(default)s")
    parser.add_argument("-l", "--lanes", dest="lanes", default='12', type=str, help="lanes to check, default %(default)s")
    parser.add_argument("-n", "--numcycles", dest="num_cycles_str", type=str, default="6,6", help="number of barcode cycles, default %(default)s")
    parser.add_argument("--numreads", dest="numreads", default=100000, type=int, help="maximum # reads to consult, default %(default)s")
    parser.add_argument("-b", "--basecalls", dest="basecalls", default=".", type=str, help="basecalls dir, default %(default)s")

    options=parser.parse_args()

    print "Options:" + str(options)

    if options.ss:
        bcs=readSampleSheetNovaSeq(options.ss)
    else:
        bcs={}

    maxSamplePerLane = max([len(v) for v in bcs.itervalues()])
    if maxSamplePerLane>=options.maxtags*.75:
        print >>sys.stderr, "WARNING: Lane seen with %d samples.  Consider increasing maxtags (-m)" % maxSamplePerLane

    num_cycles=[int(e) for e in options.num_cycles_str.split(',')]

    for lane in options.lanes:
        expected_found=expected_notfound=found_expected=found_notexpected = 0
        tags={}
        total=0

        for tag in novaSeqReader(lane, options.basecalls, num_cycles):
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
