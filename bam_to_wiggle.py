#!/usr/bin/env python
"""Convert BAM files to BigWig file format in a specified region.

Usage:
    bam_to_wiggle.py <BAM file> [<YAML config>]
    [--outfile=<output file name>]

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
import tempfile
from optparse import OptionParser
from contextlib import contextmanager, closing

import pysam


def main(bam_file, chrom='all', start=0, end=None,
         outfile=None):
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
        # Use a temp file to avoid any possiblity of not having write
        # permission
        wig_file_f = "%s.f.wig" % os.path.splitext(outfile)[0]
        wig_file_r = "%s.r.wig" % os.path.splitext(outfile)[0]
        out_handle_f = open(wig_file_f, "w")
        out_handle_r = open(wig_file_r, "w")

        with closing(out_handle_f) and closing(out_handle_r):
            write_bam_track(bam_file, regions, out_handle_f, out_handle_r)


@contextmanager
def indexed_bam(bam_file):
    if not os.path.exists(bam_file + ".bai"):
        pysam.index(bam_file)
    sam_reader = pysam.Samfile(bam_file, "rb")
    yield sam_reader
    sam_reader.close()


def write_bam_track(bam_file, regions, out_handle_f, out_handle_r):
    header = "track %s\n" % " ".join(
        [
            "type=wiggle_0",
            "name=%s" % os.path.splitext(os.path.split(bam_file)[-1])[0],
            "visibility=full",
        ]
    )
    out_handle_f.write(header)
    out_handle_r.write(header)
    with indexed_bam(bam_file) as work_bam:
        sizes = zip(work_bam.references, work_bam.lengths)
        if len(regions) == 1 and regions[0][0] == "all":
            regions = [(name, 0, length) for name, length in sizes]
        for chrom, start, end in regions:
            if end is None and chrom in work_bam.references:
                end = work_bam.lengths[work_bam.references.index(chrom)]
            assert end is not None, "Could not find %s in header" % chrom
            out_handle_f.write("variableStep chrom=%s\n" % chrom)
            out_handle_r.write("variableStep chrom=%s\n" % chrom)

            # Since the file is sorted, we could actually optimise this bit
            # out...currently fails cost benefit analysis so will wait until
            # memory issues are reported.
            start_map_f = {}
            start_map_r = {}

            for col in work_bam.fetch(chrom, start, end):
                if col.is_reverse:
                    start = col.qstart + col.rlen
                    if start in start_map_r:
                        start_map_r[start] += 1
                    else:
                        start_map_r[start] = 1
                else:
                    start = col.qend
                    if start in start_map_f:
                        start_map_f[start] += 1
                    else:
                        start_map_f[start] = 1
            # Write to file
            for i in range(start, end):
                if i in start_map_f:
                    out_handle_f.write("%s %.1f\n" % (i, start_map_f[i]))
                else:
                    out_handle_f.write("%s 0.0\n" % i)
            for i in range(start, end):
                if i in start_map_r:
                    out_handle_r.write("%s %.1f\n" % (i, start_map_r[i]))
                else:
                    out_handle_r.write("%s 0.0\n" % i)


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
        start=0)
    main(*args, **kwargs)
