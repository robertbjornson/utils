import sys, os, shutil, subprocess, gzip, argparse

epilog='''

This script takes a directory tree that contains quip compressed files somewhere within it, and
creates a copy of the entire directory tree, changing the quip'd files to either fastq or compressed
fastq.
'''
   
parser=argparse.ArgumentParser(epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-c", "--compress", action="store_true", dest="compress", default=False, help="generate compressed fastq files")
parser.add_argument("-a", "--all", action="store_true", dest="all", default=False, help="copy all files (by default only .qp files are copied)")
parser.add_argument("-n", "--dryrun", action="store_true", dest="dryrun", default=False, help="dryrun, don't do anything")
parser.add_argument("fromdir", help="source directory")
parser.add_argument("destdir", help="dest directory")

options=parser.parse_args()

prefixlen=len(options.fromdir)

for d, dirs, files in os.walk(options.fromdir):
  
  dd=options.destdir+d[prefixlen:]
  print "creating %s" % dd 
  if not options.dryrun: os.mkdir(dd)
  for f in files:
      ff="%s/%s" % (d, f)

      if f.endswith(".qp"):
          quipfile=True
          if options.compress:
              tf="%s/%s" % (dd, f[:-3]+".gz")
          else:
              tf="%s/%s" % (dd, f[:-3]+".txt")
      else:
          if not options.all: continue
          quipfile=False
          tf="%s/%s" % (dd, f)

      print "converting %s -> %s" % (ff, tf)
      if options.dryrun: continue
      if quipfile:
          ofp=open(tf, 'w')
          if options.compress:
              p1 = subprocess.Popen(["/home/bioinfo/software/Quip/bin/quip", '-c', '-d', ff], stdout=subprocess.PIPE)
              p2 = subprocess.call(["/bin/gzip", '-c'], stdin=p1.stdout, stdout=ofp)
          else:
              p1 = subprocess.call(["/home/bioinfo/software/Quip/bin/quip", '-c', '-d', ff], stdout=ofp)

      else:
          shutil.copy2(ff, tf)

