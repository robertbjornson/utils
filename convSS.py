
# this script takes a samplesheet with index IDs and replaces them with the actual barcodes

import sys, re
import index2barcode

fp=open(sys.argv[1])
hdr=fp.readline()
print hdr,

Apat=re.compile("A(\d\d\d)")

for l in fp:
    ee=l.rstrip().split(',')
    ee=[e.strip() for e in ee]
    try:
        # test whether it's dual indexed, both integers
        idx4=int(ee[4])
        idx5=int(ee[5])
        ee[4]=index2barcode.index2barcode[ee[4]]
        ee[5]=index2barcode.index2barcode[ee[5]]
        print ','.join(ee)
        continue
    except:
        pass
    try:
        # test whether it's an integer
        idx=int(ee[4])
        ee[4]=index2barcode.index2barcode[ee[4]]
        print ','.join(ee)
        continue
    except:
        pass
    try:
        ee[4]=index2barcode.index2barcode[str(int(Apat.match(ee[4]).groups()[0]))]
        print ','.join(ee)
        continue
    except:
        pass
    print ','.join(ee)
    
