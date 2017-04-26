import sys
for l in sys.stdin:
    e=l.strip().split(',')
    nw=e[0:4]+[e[4]+'-'+e[5]]+e[6:]
    print ','.join(nw)
