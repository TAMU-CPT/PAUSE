#!/usr/bin/env python
"""Extract read start from BAM files to Wig format for PAUSE.

Usage:
    bam_to_wiggle.py <BAM file>

"""
import os
import sys
import bx.wiggle
import numpy
import pysam
from galaxygetopt.ggo import GalaxyGetOpt as GGO


def get_data(wig_handle):
    data = []
    for row in bx.wiggle.Reader(wig_handle):
        data.append((row[1], row[2]))

    reshaped = numpy.array(data, dtype=numpy.int)
    return reshaped


def main(starts_f=None, starts_r=None, bam_file=None, **kwd):
    data_f = get_data(starts_f)
    data_r = get_data(starts_r)
    (max_f, min_f) = peakdet(data_f[:, 1], 10)
    (max_r, min_r) = peakdet(data_r[:, 1], 10)
    return (max_f, max_r)


def peakdet(v, delta, x=None):
    # https://gist.github.com/endolith/250860
    """
    Converted from MATLAB script at http://billauer.co.il/peakdet.html

    Returns two arrays

    function [maxtab, mintab]=peakdet(v, delta, x)
    %PEAKDET Detect peaks in a vector
    %        [MAXTAB, MINTAB] = PEAKDET(V, DELTA) finds the local
    %        maxima and minima ("peaks") in the vector V.
    %        MAXTAB and MINTAB consists of two columns. Column 1
    %        contains indices in V, and column 2 the found values.
    %
    %        With [MAXTAB, MINTAB] = PEAKDET(V, DELTA, X) the indices
    %        in MAXTAB and MINTAB are replaced with the corresponding
    %        X-values.
    %
    %        A point is considered a maximum peak if it has the maximal
    %        value, and was preceded (to the left) by a value lower by
    %        DELTA.

    % Eli Billauer, 3.4.05 (Explicitly not copyrighted).
    % This function is released to the public domain; Any use is allowed.

    """
    maxtab = []
    mintab = []

    if x is None:
        x = numpy.arange(len(v))

    v = numpy.asarray(v)

    if len(v) != len(x):
        sys.exit('Input vectors v and x must have same length')

    if not numpy.isscalar(delta):
        sys.exit('Input argument delta must be a scalar')

    if delta <= 0:
        sys.exit('Input argument delta must be positive')

    mn, mx = numpy.Inf, -numpy.Inf
    mnpos, mxpos = numpy.NaN, numpy.NaN

    lookformax = True

    for i in numpy.arange(len(v)):
        this = v[i]
        if this > mx:
            mx = this
            mxpos = x[i]
        if this < mn:
            mn = this
            mnpos = x[i]

        if lookformax:
            if this < mx-delta:
                maxtab.append((mxpos, mx))
                mn = this
                mnpos = x[i]
                lookformax = False
        else:
            if this > mn+delta:
                mintab.append((mnpos, mn))
                mx = this
                mxpos = x[i]
                lookformax = True

    return numpy.array(maxtab, dtype=numpy.int), numpy.array(mintab,
                                                             dtype=numpy.int)


if __name__ == "__main__":
    opts = GGO(
        options=[
            ['starts_f', '+ strand start wig data',
             {'required': True, 'validate': 'File/Input'}],
            ['starts_r', '- strand start wig data',
             {'required': True, 'validate': 'File/Input'}],
            ['bam_file', 'Bam File',
             {'required': True, 'validate': 'File/Input'}],
        ],
        outputs=[
            [
                'wig_f',
                '+ strand PAUSE wig results',
                {
                    'validate': 'File/Output',
                    'required': True,
                    'default': 'wig.pause.f',
                    'data_format': 'text/plain',
                    'default_format': 'TXT',
                }
            ],
            [
                'wig_r',
                '- strand PAUSE wig results',
                {
                    'validate': 'File/Output',
                    'required': True,
                    'default': 'wig.pause.r',
                    'data_format': 'text/plain',
                    'default_format': 'TXT',
                }
            ],
            [
                'pause_report',
                'PAUSE Report',
                {
                    'validate': 'File/Output',
                    'required': True,
                    'default': 'pause_report',
                    'data_format': 'text/plain',
                    'default_format': 'TXT',
                }
            ]
        ],
        defaults={
            'appid': 'edu.tamu.cpt.pause2.analysis',
            'appname': 'PAUSE2 Analaysis',
            'appvers': '0.1',
            'appdesc': 'run PAUSE analysis',
        },
        tests=[],
        doc=__doc__
    )
    options = opts.params()
    (f, r) = main(**options)

    if not os.path.exists(options['bam_file'].name + ".bai"):
        pysam.index(options['bam_file'].name)
    sam_reader = pysam.Samfile(options['bam_file'].name, "rb")
    sizes = zip(sam_reader.references, sam_reader.lengths)
    regions = [(name, 0, length) for name, length in sizes]
    header = """track type=wiggle_0 name=%s visibility=full
variableStep chrom=%s\n"""

    data_f = header % ('highlights_f', regions[0][0])
    for row in f:
        data_f += ' '.join(map(str, row)) + "\n"

    data_r = header % ('highlights_r', regions[0][0])
    for row in r:
        data_r += ' '.join(map(str, row)) + "\n"

    from galaxygetopt.outputfiles import OutputFiles
    off = OutputFiles(name='wig_f', GGO=opts)
    off.CRR(data=data_f)
    ofr = OutputFiles(name='wig_r', GGO=opts)
    ofr.CRR(data=data_r)
