##############################################################################
#                                                                            #
#    Convert and filter SAM formatted input stream to a pickled list.        #
#    Copyright(C) 2013  TU Delft & VU University Medical Center Amsterdam    #
#    Author: Roy Straver, r.straver@vumc.nl                                  #
#                                                                            #
#    This file is part of WISECONDOR.                                        #
#                                                                            #
#    WISECONDOR is free software: you can redistribute it and/or modify      #
#    it under the terms of the GNU General Public License as published by    #
#    the Free Software Foundation, either version 3 of the License, or       #
#    (at your option) any later version.                                     #
#                                                                            #
#    WISECONDOR is distributed in the hope that it will be useful,           #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of          #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
#    GNU General Public License for more details.                            #
#                                                                            #
#    You should have received a copy of the GNU General Public License       #
#    along with WISECONDOR.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                            #
##############################################################################



import sys
import pickle
import argparse

parser = argparse.ArgumentParser(description='Convert any stream of reads to a pickle file for WISECONDOR, defaults are set for the SAM format',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('-infile', type=str,
                    help='')
parser.add_argument('-outfile', type=str,
                    help='reference table output, used for sample testing (pickle)')

parser.add_argument('-keepfile', type=str,
                    help='unaltered output of reads used in analysis')
parser.add_argument('-dropfile', type=str,
                    help='unaltered output of reads ignored in analysis')
parser.add_argument('-keepprint', action='store_true',
                    help='unaltered output of reads used in analysis to stdout')

parser.add_argument('-binsize', type=int, default=50000,
                    help='binsize used for samples')
parser.add_argument('-retdist', type=int, default=4,
                    help='maximum amount of base pairs difference between sequential reads to consider them part of the same tower')
parser.add_argument('-retthres', type=int, default=4,
                    help='threshold for when a group of reads is considered a tower and will be removed')    # negative to keep all

args = parser.parse_args()

binsize     = args.binsize
minShift    = args.retdist
threshold   = args.retthres

# Prepare the list of chromosomes
chromosomes = dict()
for chromosome in range(1,23):
    chromosomes[str(chromosome)] = [0]
chromosomes['X'] = [0]
chromosomes['Y'] = [0]

if args.keepfile:
    fileKeep = open(args.keepfile,'w')
if args.dropfile:
    fileDrop = open(args.dropfile,'w')

# Flush the current stack of reads
def flush(readBuff):
    global chromosomes
    stairSize = len(readBuff)
    if stairSize <= threshold or threshold < 0: 
        for read in readBuff:
            chromosome = read[0][3:]
            location = read[1]
            bin        = location/binsize       # index of the bin the read belongs to
            if (chromosome in chromosomes):     # ????
                chromosomes[chromosome].extend([0.] * (bin - len(chromosomes[chromosome]) + 1))
                chromosomes[chromosome][bin] += 1
        if args.keepfile:
            for line in fullBuff:
                fileKeep.write(line)
        if args.keepprint:
            for line in fullBuff:
                    print line
    elif args.dropfile:
        for line in fullBuff:
            fileDrop.write(line)
                
                        
prevWords = ['0'] * 10
readBuff = []
fullBuff = []

# for each line in sam file
#for line in sys.stdin:
f = open('part.sam', 'r')
for line in f:
    curWords = line.split()

    # Not ndup, flush and start new stair
    if not((curWords[2] == prevWords[2]) and (minShift >= (int(curWords[3])-int(prevWords[3])))):
        flush(readBuff)
        readBuff = []
        fullBuff = []

    readBuff.append([curWords[2],int(curWords[3])])
    fullBuff.append(line)
    
    prevWords = curWords
    prevLine = line

# Flush after we're done
flush(readBuff)
f.close()

# Dump converted data to a file
if args.outfile:
    pickle.dump(chromosomes,open(args.outfile,'wb'))

if args.keepfile:
    fileKeep.close()
if args.dropfile:
    fileDrop.close()
