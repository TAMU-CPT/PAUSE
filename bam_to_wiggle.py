#!/usr/bin/env python
"""Convert BAM files to BigWig file format in a specified region.

Usage:
    bam_to_wiggle.py <BAM file> [<YAML config>]
    [--outfile=<output file name>
     --chrom=<chrom>
     --start=<start>
     --end=<end>
     --normalize]

chrom start and end are optional, in which case they default to everything.
The normalize flag adjusts counts to reads per million.

The config file is in YAML format and specifies the location of the wigToBigWig
program from UCSC:

program:
  ucsc_bigwig: wigToBigWig

If not specified, these will be assumed to be present in the system path.

The script requires:
    pysam (http://code.google.com/p/pysam/)
    wigToBigWig from UCSC (http://hgdownload.cse.ucsc.edu/admin/exe/)
If a configuration file is used, then PyYAML is also required
(http://pyyaml.org/)
"""
import os
import sys
import subprocess
import tempfile
from optparse import OptionParser
from contextlib import contextmanager, closing

import pysam


def main(bam_file, chrom='all', start=0, end=None,
         outfile=None, normalize=False, use_tempfile=False):
    if outfile is None:
        outfile = "%s.bigwig" % os.path.splitext(bam_file)[0]
    if start > 0:
        start = int(start) - 1
    if end is not None:
        end = int(end)
    regions = [(chrom, start, end)]
    if os.path.abspath(bam_file) == os.path.abspath(outfile):
        sys.stderr.write("Bad arguments, input and output files are the same.\n")
        sys.exit(1)
    if not (os.path.exists(outfile) and os.path.getsize(outfile) > 0):
        if use_tempfile:
            #Use a temp file to avoid any possiblity of not having write permission
            out_handle = tempfile.NamedTemporaryFile(delete=False)
            wig_file = out_handle.name
        else:
            wig_file = "%s.wig" % os.path.splitext(outfile)[0]
            out_handle = open(wig_file, "w")
        with closing(out_handle):
            chr_sizes, wig_valid = write_bam_track(bam_file, regions, out_handle,
                                                   normalize)


@contextmanager
def indexed_bam(bam_file):
    if not os.path.exists(bam_file + ".bai"):
        pysam.index(bam_file)
    sam_reader = pysam.Samfile(bam_file, "rb")
    yield sam_reader
    sam_reader.close()


def write_bam_track(bam_file, regions, out_handle, normalize):
    out_handle.write("track %s\n" % " ".join(["type=wiggle_0",
        "name=%s" % os.path.splitext(os.path.split(bam_file)[-1])[0],
        "visibility=full",
        ]))
    is_valid = False
    with indexed_bam(bam_file) as work_bam:
        sizes = zip(work_bam.references, work_bam.lengths)
        if len(regions) == 1 and regions[0][0] == "all":
            regions = [(name, 0, length) for name, length in sizes]
        for chrom, start, end in regions:
            if end is None and chrom in work_bam.references:
                end = work_bam.lengths[work_bam.references.index(chrom)]
            assert end is not None, "Could not find %s in header" % chrom
            out_handle.write("variableStep chrom=%s\n" % chrom)
            for col in work_bam.pileup(chrom, start, end):
                out_handle.write("%s %.1f\n" % (col.pos+1, col.n))
                is_valid = True
    return sizes, is_valid


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-o", "--outfile", dest="outfile")
    (options, args) = parser.parse_args()
    if len(args) != 1:
        print "Incorrect arguments"
        print __doc__
        sys.exit()
    kwargs = dict(
        outfile=options.outfile,
        chrom='all',
        start=0,
        normalize=False,
        use_tempfile=False)
    main(*args, **kwargs)
