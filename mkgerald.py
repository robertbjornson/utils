
import sys, collections

template='''
EMAIL_LIST robert.bjornson@yale.edu
EMAIL_SERVER mail.yale.edu
EMAIL_DOMAIN yale.edu
USE_BASES Y*
ELAND_FASTQ_FILES_PER_PROCESS 3

%s

REFERENCE mouse ELAND_GENOME /sequencers/haifan_lin/genomes/iGenome/Mus_musculus/Ensembl/NCBIM37/Sequence/Chromosomes
REFERENCE mouse ELAND_RNA_GENOME_ANNOTATION /sequencers/haifan_lin/genomes/iGenome/Mus_musculus/Ensembl/NCBIM37/Annotation/Genes/refFlat.txt.gz 
REFERENCE mouse ELAND_RNA_GENOME_CONTAM /sequencers/haifan_lin/genomes/iGenome/Mus_musculus/Ensembl/NCBIM37/Sequence/AbundantSequences

REFERENCE human ELAND_GENOME /sequencers/haifan_lin/genomes/iGenome/Homo_sapiens/Ensembl/GRCh37/Sequence/Chromosomes
REFERENCE human ELAND_RNA_GENOME_ANNOTATION /sequencers/haifan_lin/genomes/iGenome/Homo_sapiens/Ensembl/GRCh37/Annotation/Genes/refFlat.txt.gz
REFERENCE human ELAND_RNA_GENOME_CONTAM /sequencers/haifan_lin/genomes/iGenome/Homo_sapiens/Ensembl/GRCh37/Sequence/AbundantSequences

REFERENCE fly ELAND_GENOME /sequencers/haifan_lin/genomes/iGenome/Drosophila_melanogaster/Ensembl/BDGP5.25/Sequence/Chromosomes
REFERENCE fly ELAND_RNA_GENOME_ANNOTATION /sequencers/haifan_lin/genomes/iGenome/Drosophila_melanogaster/Ensembl/BDGP5.25/Annotation/Genes/refFlat.txt.gz
REFERENCE fly ELAND_RNA_GENOME_CONTAM /sequencers/haifan_lin/genomes/iGenome/Drosophila_melanogaster/Ensembl/BDGP5.25/Sequence/AbundantSequences

REFERENCE pombe ELAND_GENOME /sequencers/haifan_lin/genomes/iGenome/Schizosaccharomyces_pombe/Ensembl/EF1/Sequence/Chromosomes
REFERENCE pombe ELAND_RNA_GENOME_ANNOTATION /sequencers/haifan_lin/genomes/iGenome/Schizosaccharomyces_pombe/Ensembl/EF1/Annotation/Genes/refFlat.txt.gz
REFERENCE pombe ELAND_RNA_GENOME_CONTAM /sequencers/haifan_lin/genomes/iGenome/Schizosaccharomyces_pombe/Ensembl/EF1/Sequence/AbundantSequences

REFERENCE e.coli ELAND_GENOME /sequencers/haifan_lin/genomes/iGenome/Escherichia_coli_K_12_DH10B/NCBI/2008-03-17/Sequence/Chromosomes
REFERENCE e.coli ELAND_RNA_GENOME_ANNOTATION /sequencers/haifan_lin/genomes/iGenome/Escherichia_coli_K_12_DH10B/NCBI/2008-03-17/Annotation/Genes/refGene.txt
REFERENCE e.coli ELAND_RNA_GENOME_CONTAM /sequencers/haifan_lin/genomes/iGenome/Escherichia_coli_K_12_DH10B/NCBI/2008-03-17/Sequence/AbundantSequences

REFERENCE c.elegans ELAND_GENOME /sequencers/haifan_lin/genomes/iGenome/Caenorhabditis_elegans/UCSC/ce6/Sequence/Chromosomes
REFERENCE c.elegans ELAND_RNA_GENOME_ANNOTATION /sequencers/haifan_lin/genomes/iGenome/Caenorhabditis_elegans/UCSC/ce6/Annotation/Genes/refFlat.txt.gz
REFERENCE c.elegans ELAND_RNA_GENOME_CONTAM /sequencers/haifan_lin/genomes/iGenome/Caenorhabditis_elegans/UCSC/ce6/Sequence/AbundantSequences

REFERENCE rat ELAND_GENOME /sequencers/haifan_lin/genomes/iGenome/Rattus_norvegicus/UCSC/rn5/Sequence/Chromosomes
REFERENCE rat ELAND_RNA_GENOME_ANNOTATION /sequencers/haifan_lin/genomes/iGenome/Rattus_norvegicus/UCSC/rn5/Annotation/Genes/refFlat.txt.gz 
REFERENCE rat ELAND_RNA_GENOME_CONTAM /sequencers/haifan_lin/genomes/iGenome/Rattus_norvegicus/UCSC/rn5/Sequence/AbundantSequences

REFERENCE phix ELAND_GENOME /sequencers/haifan_lin/genomes/iGenome/PhiX/Illumina/RTA/Sequence/Chromosomes
'''

p2a=collections.OrderedDict()

fp=open(sys.argv[1])
hdr=fp.readline()

for l in fp:
    FCID,Lane,SampleID,SampleRef,Index,Description,Control,Recipe,Operator,SampleProject=l.rstrip().split(',')
    Recipe=Recipe.lower()
    Recipe={'eland_ext':'eland_extended'}.get(Recipe,Recipe) 
    r=p2a.get(SampleProject, None)
    if r:
        if r==Recipe: 
            continue
        else:
            print sys.stderr, "Error: Project %s has multiple analyses specified" % SampleProject
            sys.exit(1)
    else:
        p2a[SampleProject]=Recipe
       

analyses="\n".join(['PROJECT %s ANALYSIS %s' % (k, v) for k, v in p2a.iteritems()])

print template % analyses
