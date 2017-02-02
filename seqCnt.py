
import sys, numpy
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
    type=sys.argv[1]
    files=sys.argv[2:]

    scnt=bcnt=0
    lens=[]
    
    if type=="-a":
        h=fastaHandler(files)
    elif type=="-q":
        h=fastqHandler(files)
    else:
        raise Exception("Unknown type")

    for l in h:
        scnt+=1
        bcnt+=l
        lens.append(l)
        
    print "seqs %d bases %d max %d min %d mean %d median %d" % (scnt, bcnt, numpy.max(lens), numpy.min(lens), numpy.mean(lens), numpy.median(lens))
    
