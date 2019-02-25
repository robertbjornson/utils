
import sys, numpy, argparse
import fasta, fastq

def fastaHandler(files):
    for f in files:
        r=fasta.fastaReader(f)
        for hdr, seq in r:
            yield len(seq)

def fastqHandler(files):
    for f in files:
        r=fastq.fastqReader(f)
        for hdr1, seq, hdr2, qual in r:
            yield len(seq)
    
if __name__=='__main__':

    parser=argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-c", "--combine", dest="combine", action="store_true", default=False, help="combine counts")
    parser.add_argument("-t", "--type", dest="type", default="q", help="input file type (a=fasta, q=fastq)")
    parser.add_argument("files", nargs=argparse.REMAINDER)

    options=parser.parse_args()

    print(options)

    print ("\tseqs\tbases\tmax\tmin\tmean\tmedian")

    if options.type=="a":
        h=fastaHandler
    elif options.type=="q":
        h=fastqHandler
    else:
        raise Exception("Unknown type")

    if options.combine:
        scnt=bcnt=0
        lens=[]
        for l in h(options.files):
            scnt+=1
            bcnt+=l
            lens.append(l)
        
        print ("Combined\t%d\t%d\t%d\t%d\t%d\t%d" % (scnt, bcnt, numpy.max(lens), numpy.min(lens), numpy.mean(lens), numpy.median(lens)))
    else:
        for f in options.files:
            scnt=bcnt=0
            lens=[]
            for l in h([f,]):
                scnt+=1
                bcnt+=l
                lens.append(l)

            print ("%s\t%d\t%d\t%d\t%d\t%d\t%d" % (f, scnt, bcnt, numpy.max(lens), numpy.min(lens), numpy.mean(lens), numpy.median(lens)))
            
    
