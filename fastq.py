
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

