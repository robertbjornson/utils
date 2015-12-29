import sys, gzip

def fastqReader(fn):
    if fn=='-':
        fp=sys.stdin
    else:
        try:
            # test to see if it's compressed
            fp=gzip.open(fn)
            test=fp.readline()
            fp.seek(0)
        except IOError:
            fp=open(fn)
    while True:
        hdr1=fp.readline().rstrip()
        if not hdr1:
            break
        assert hdr1.startswith('@')
        seq=fp.readline().rstrip()
        hdr2=fp.readline().rstrip()
        assert hdr2.startswith('+')
        qual=fp.readline().rstrip()
        yield (hdr1, seq, hdr2, qual)

class fastqWriter:
    def __init__(self, fn, linelen=60):
        self.ofile=open(fn, 'w')
        self.linelen=linelen
    def close(self):
        self.ofile.close()
    def writeFQ(self, hdr1, seq, hdr2, qual):
        pos=0
        assert(len(seq)==len(qual))
        stop=len(seq)
        self.ofile.write(hdr1)
        self.ofile.write('\n')
        while pos<stop:
            self.ofile.write(seq[pos:pos+self.linelen])
            self.ofile.write('\n')
            pos+=self.linelen

        pos=0
        stop=len(qual)
        self.ofile.write(hdr2)
        self.ofile.write('\n')
        while pos<stop:
            self.ofile.write(qual[pos:pos+self.linelen])
            self.ofile.write('\n')
            pos+=self.linelen

if __name__=='__main__':
    rdr=fastqReader(sys.argv[1])
    wrter=fastqWriter(sys.argv[2], 9999)
    for hdr1, seq, hdr2, qual in rdr:
        wrter.writeFQ(hdr1, seq, hdr2, qual)
    wrter.close()
