
'''
Copyright 2012, Robert Bjornson, Yale University

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Ths program takes an Illumina samplesheet (old style, v1.8) and a config file (aka gerald.txt), and compares them to
make sure everything matches up.
'''


import re, sys, optparse, os

def parseSample(fn):
    fp=open(fn)
    head=fp.readline()
    sample_d={}
    for l in fp:
        try:
            s=dict(zip(['fcid', 'lane', 'id', 'ref', 'index', 'desc', 'cont', 'recipe', 'operator', 'project'], l.rstrip().split(',')))
            sample_d.setdefault(s['lane'], []).append(s)
        except ValueError:
            warning("Couldn't parse sample line: %s" % l.rstrip())

    return sample_d

def parseGerald(fn):
    cats=['PROJECT', 'REFERENCE', 'SAMPLE', 'BARCODE', 'lane', 'default']
    cat_d={}
    def_d={}

    comment_pat=re.compile('^#')
    skip_pat=re.compile('^#*\s*$')
    def_pat=re.compile('^(\S+)\s+(\S+)\s*$')
    lane_pat=re.compile('^([12345678]+):\s*(\S+)\s+(\S+)$')
    cat_pat=re.compile('^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*$')
    fp=open(fn)
    for l in fp:
        mo=skip_pat.match(l)
        if mo: continue
        mo=comment_pat.match(l)
        if mo: continue
        mo=lane_pat.match(l)
        if mo:
            lanes, param, paramval = mo.groups()
            for lane in lanes:
                cat_d.setdefault('LANE', {}).setdefault(lane, {}).setdefault(param, paramval)
            continue
        mo=def_pat.match(l)
        if mo:
            param, val = mo.groups()
            def_d[param]=val
            continue
        mo=cat_pat.match(l)
        if mo:
            cat, catval, param, paramval = mo.groups()
            cat_d.setdefault(cat, {}).setdefault(catval, {}).setdefault(param, paramval)
            continue
        warning("Couldn't parse gerald line: %s" % l.rstrip())
            
    return def_d, cat_d

#barcode_pat=re.compile('^[ACGT]{6}$')
#barcode_pat=re.compile('^[ACGT-]{6,17}$')
barcode_pat=re.compile('^[ACGT]{6,8}(-[ACGT]{6,8})?$')

def check_path(arg):
    return os.path.exists(arg)

def check_fasta(arg):
    return int(arg) >= 3 and int(arg) <= 4

def check_analysis(arg):
    return arg in ['eland_extended', 'eland_pair', 'eland_rna', 'none']

parameter_validation={
    'ELAND_GENOME': check_path,
    'ELAND_RNA_GENOME_CONTAM': check_path,
    'ELAND_RNA_GENOME_ANNOTATION': check_path,
    'ELAND_FASTQ_FILES_PER_PROCESS': check_fasta,
    'ANALYSIS': check_analysis,
}

def warning(msg):
    global final_ok
    final_ok=False
    print "WARNING: %s" % msg

def isValidBarcode(bc):
    return barcode_pat.match(bc) and True

def validate_samples(options, sample_d, def_d, cat_d):
    all_reqs=['USE_BASES', 'ANALYSIS', 'ELAND_FASTQ_FILES_PER_PROCESS']

    if len(sample_d) != 8:
        warning('Expected values for 8 lanes in samplesheet')
    for lane_k, lane_v in sample_d.iteritems():
        # if lane has more than 1 sample, require barcodes for all samples in lane
        if len(lane_v) > 1:
            for sample in lane_v:
                if not isValidBarcode(sample['index']):
                    warning('Expected barcode for sample %s' % sample['id'])
        for sample in lane_v:
            sample['params']=sample_params=def_d.copy()
            sample_params.update(cat_d.get('LANE',{}).get(sample['lane'],{}))
            sample_params.update(cat_d.get('BARCODE',{}).get(sample['index'],{}))
            sample_params.update(cat_d.get('SAMPLE',{}).get(sample['id'],{}))
            sample_params.update(cat_d.get('REFERENCE',{}).get(sample['ref'],{}))
            sample_params.update(cat_d.get('PROJECT',{}).get(sample['project'],{}))
                
            for req in all_reqs:
                if req not in sample_params:
                    warning("required param %s not found in %s" % (req, sample['id']))

            for param, test in parameter_validation.iteritems():
                if sample_params.has_key(param) and not test(sample_params[param]):
                    warning("Parameter %s failed %s on %s in sample %s lane %s" % (param, test.__name__, sample_params[param], sample['id'], sample['lane']))
                        
            if sample_params.get('ANALYSIS', "") != 'none' and 'ELAND_GENOME' not in sample_params:
                warning("required param %s not found in %s" % ('ELAND_GENOME', sample['id']))

            if sample_params.get('ANALYSIS', "") == 'eland_rna':
                for req in ['ELAND_RNA_GENOME_ANNOTATION', 'ELAND_RNA_GENOME_CONTAM']:
                    if req not in sample_params:
                        warning("required param %s not found in %s" % (req, sample['id']))

if __name__=='__main__':

    final_ok=True
    
    parser=optparse.OptionParser()
    parser.add_option("-s", "--samplesheet", dest="ss", help="samplesheet file")
    parser.add_option("-c", "--config", dest="gerald", help="config file")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", help="verbose")

    (options, args) = parser.parse_args()

    if options.verbose:
        print "Invocation: " + " ".join(sys.argv)
        print "Options:" + str(options)

    def_d, cat_d=parseGerald(options.gerald)
    sample_d=parseSample(options.ss)
    validate_samples(options, sample_d, def_d, cat_d)

    if options.verbose:
        #SDU of samples
        for l, sample_list in sorted(sample_d.iteritems()):
            sorted_samples = [s for p, i, s in sorted([(s['project'], s['id'], s) for s in sample_list])]
            for sample in sorted_samples:
                print '\t'.join([sample[f] for f in ['project', 'id', 'lane']])
                for k,v in sample['params'].iteritems():
                    print "%s\t%s" % (k,v)
                print
            
    if final_ok:
        print "Looks OK"
    else:
        print "There were some problems, please fix"
        
# todo
# add actual barcodes
# add check of paths
# add ok/bad, verbose flag
