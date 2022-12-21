

'''
Snapshots in file system fs0: [data and metadata]
Directory                SnapId    Status  Created                   Fileset           Data  Metadata
20221217-0326            872       Valid   Sat Dec 17 03:26:02 2022  root            46.44T    324.2G
20221218-0335            873       Valid   Sun Dec 18 03:35:02 2022  root            4.046T    56.34G
20221219-0349            874       Valid   Mon Dec 19 03:49:03 2022  root            3.447T     80.1G
20221220-0349            875       Valid   Tue Dec 20 03:49:02 2022  root            4.329T    74.08G

sadly not separated by \ts
['20221217-0326', '872', 'Valid', 'Sat', 'Dec', '17', '03:26:02', '2022', 'root', '46.44T', '324.2G']
'''

mult={'B':1.0/1024.0**4, 'K':1.0/1024.0**3, 'M':1.0/1024.0**2, 'G':1.0/1024.0**1, 'T':1.0}

def conv(v):
  if v[-1] in 'KMGT':
    r=float(v[:-1])*mult[v[-1]]
  else:
    r=float(v)*mult['B']
  return r

sumData={}
sumMeta={}

import sys

for l in open(sys.argv[1]).readlines()[2:]:
  ts, id, status, day, month, date, time, year, fileset, data, meta = l.strip().split()[:11]
  if status != 'Valid': continue
  data = conv(data)
  meta = conv(meta)
  sumData[fileset]=sumData.get(fileset, 0.0)+data    
  sumMeta[fileset]=sumMeta.get(fileset, 0.0)+meta

for fs in sumData:
  print("%s\t%f\t%f" % (fs, sumData[fs], sumMeta[fs]))

