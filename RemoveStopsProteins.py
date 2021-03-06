#-----------------------------------------------------------+
#                                                           |
# RemoveStopsProteins.py - Removes the proteins with stops  |
#                                                           |
#-----------------------------------------------------------+
#                                                           |
# AUTHOR: Vikas Gupta                                       |
# CONTACT: vikas0633@gmail.com                              |
# STARTED: 09/06/2013                                       |
# UPDATED: 09/06/2013                                       |
#                                                           |
# DESCRIPTION:                                              | 
#                                                           |
# LICENSE:                                                  |
#  GNU General Public License, Version 3                    |
#  http://www.gnu.org/licenses/gpl.html                     |  
#                                                           |
#-----------------------------------------------------------+

# Example:
# python ~/script/python/100b_fasta2flat.py -i 02_Stegodyphous_cdna.refined.fa.orf.tr_longest_frame


### import modules
import os,sys,getopt, re


### global variables

### make a logfile
import datetime
now = datetime.datetime.now()
o = open(str(now.strftime("%Y-%m-%d_%H%M."))+'logfile','w')



### write logfile

def logfile(infile):
    o.write("Program used: \t\t%s" % "100b_fasta2flat.py"+'\n')
    o.write("Program was run at: \t%s" % str(now.strftime("%Y-%m-%d_%H%M"))+'\n')
    o.write("Infile used: \t\t%s" % infile+'\n')
            
    
def help():
    print '''
            python 100b_fasta2flat.py -i <ifile>
            '''
    sys.exit(2)

### main argument to 

def options(argv):
    gff3 = ''
    cds=''
    protein = ''
    try:
        opts, args = getopt.getopt(argv,"hi:c:p:",["ifile=","CDS=","proteins="])
    except getopt.GetoptError:
        help()
    for opt, arg in opts:
        if opt == '-h':
            help()
        elif opt in ("-i", "--ifile"):
            gff3 = arg
        elif opt in ("-c", "--CDS"):
            cds = arg
        elif opt in ("-p", "--proteins"):
            proteins = arg
            
    logfile(gff3)
            
    return gff3, cds, proteins

### split line
def split_line(line):
    return line.strip().split('\t')

### get ID
def get_ID(line):
    line = line.strip()
    match = re.search(r'ID=.+;',line)
    if match:
        return match.group().split(';')[0].replace('ID=','')
    else:
        print 'Error at line'
        print line
        sys.exit('ID is missing in the attributes')
    
### get PARENT ID
def get_PARENT(line):
    line = line.strip()
    match = re.search(r'Parent=.+',line)
    if match:
        return match.group().split(';')[0].replace('Parent=','')
    else:
        print 'Error at line'
        print line
        sys.exit('Parent ID is missing in the attributes')
    
### http://www.sequenceontology.org/gff3.shtml
### make a class that returns columns of a GFF3 row
class GFF3:
    def __init__(self, line):
        
        tokens = split_line(line)
        
        self.seqid = tokens[0]
        self.source = tokens[1]
        self.type = tokens[2]
        self.start = tokens[3]
        self.end = tokens[4]
        self.score = tokens[5]
        self.strand = tokens[6]
        self.phase = tokens[7]
        self.attribute = tokens[8]
        
        self.id = get_ID(line)
        
    def __str__(self):
        return self.id
    
    def seqids(self):
        return self.seqid
    
    def sources(self):
        return self.source
        
    def types(self):
        return self.type
    
    def starts(self):
        return self.start
    
    def ends(self):
        return self.end
    
    def scores(self):
        return self.score
    
    def strands(self):
        return self.strand
    
    def phases(self):
        return self.phase
    
    def attributes(self):
        return self.attribute

def process_objs(obj, source):
    return obj.seqids() + '\t' + \
    source + '\t' + \
    obj.types() + '\t' + \
    obj.starts() + '\t' + \
    obj.ends() + '\t' + \
    obj.scores() + '\t' + \
    obj.strands() + '\t' + \
    obj.phases() + '\t' + \
    obj.attributes()
   
def findStops(proteins):
    no_stops = {}
    no_stops_genes = {}
    stops = {}
    stops_genes = {}
    for line in open(proteins,'r'):
        line = line.strip()
        if len(line) > 1:
            if line.startswith('>'):
                header = line.split(',')[0][1:]
            else:
                if re.search('\.',line[:-2]):
                    stops[header] = ''
                    stops_genes[header[:-2]] = ''
                else:
                    no_stops[header] = ''
                    no_stops_genes[header[:-2]] = ''
            
    return stops, stops_genes, no_stops, no_stops_genes

def fixCDS(file, stops):
    o = open(file+'.updated','w')
    flag = True
    for line in open(file,'r'):
        line = line.strip()
        if line.startswith('>'):
            header = line.split(',')[0][1:]
            if header in stops:
                flag = False
            else:
                flag = True
        if flag == True:
            if line.startswith('>'):
                o.write(line+'\n')
            else:
                o.write(line.split('.')[0]+'\n')
            
    o.close()


def fixGFF3(file, stops, stops_genes, no_stops, no_stops_genes):
    o = open(file+'.updated','w')
    for line in open(file, 'r'):
        if len(line) > 1:
            line = line.strip()
            obj = GFF3(line)
            
            if obj.sources() == 'lj_r30.fa':
                if (source != 'tRNA') or (source != 'rRNA'):
                    source = "protein_coding"
            else:
                source = obj.sources()
            
            if obj.types() == 'gene':
                if str(obj) in stops_genes:
                    source = 'processed_transcript'
                elif str(obj) in no_stops_genes:
                    source = "protein_coding"
                
                elif str(obj) not in no_stops_genes:
                    if (source != 'tRNA') and (source != 'rRNA'):
                        source = 'processed_transcript'
                    
            elif obj.types() == 'mRNA':
                if str(obj) in stops:
                    source = 'processed_transcript'
                elif str(obj) in no_stops:
                    source = "protein_coding"
                
                elif str(obj) not in no_stops_genes:
                    if (source != 'tRNA') and (source != 'rRNA'):
                        source = 'processed_transcript'
                
            else:
                if get_PARENT(line) in stops:
                    source = 'processed_transcript'
                
            o.write(process_objs(obj,source)+'\n')
    o.close()
    
if __name__ == "__main__":
    
    gff3, cds, proteins = options(sys.argv[1:])
    
    ### find proteins with stops
    stops, stops_genes, no_stops, no_stops_genes = findStops(proteins)
    
    ### fix CDS file
    fixCDS(cds, stops)
    
    ### fix protein file
    fixCDS(proteins, stops)
    
    ### fix GFF3 file
    fixGFF3(gff3, stops, stops_genes, no_stops, no_stops_genes)
    
    ### close the logfile
    o.close()