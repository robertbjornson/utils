import sys

go=False
for l in open(sys.argv[1]):
    l=l.strip()
    if go:
        e=l.split(',')
        if not e[1].startswith('Sample_'):
            e[1]='Sample_'+e[1]
        if not e[9].startswith('Project_'):
            e[9]='Project_'+e[9]
        l=','.join(e)

    if l.startswith("Lane,"):
        go=True

    print l
