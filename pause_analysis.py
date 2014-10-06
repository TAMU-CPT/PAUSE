#!/usr/bin/env python
"""Extract read start from BAM files to Wig format for PAUSE.

Usage:
    bam_to_wiggle.py <BAM file>

"""
import sys
import bx.wiggle
import numpy
import pause_gfx
from galaxygetopt.ggo import GalaxyGetOpt as GGO


def main(coverage=None, starts=None):
    if coverage is None:
        coverage = []
    if starts is None:
        starts = []

    track_list = []
    count = 0

    # Coverage is handled separately and "just for looks"
    for wig_handle in coverage:
        y_vals = numpy.asarray([f[2] for f in
                                bx.wiggle.Reader(wig_handle)],
                               dtype=numpy.int)

        x_vals = range(len(y_vals))
        if count % 2 == 0:
            reshaped = numpy.column_stack((x_vals, y_vals))
        else:
            reshaped = numpy.column_stack((x_vals, -y_vals))

        #reshaped = pause_gfx.Filter.repeat_reduction(
            #pause_gfx.Filter.minpass(reshaped, min_value=2))
        track_list.append(pause_gfx.Coverage(reshaped))
        count += 1

    # Starts are handled separately from coverage
    for wig_handle in starts:
        y_vals = numpy.asarray([f[2] for f in
                                bx.wiggle.Reader(wig_handle)],
                               dtype=numpy.int)

        x_vals = range(len(y_vals))
        # Only use maxtab as mintab is always zero and basically
        # useless.
        (maxtab, mintab) = peakdet(y_vals, 20)

        # Assume datasets are given (+ strand, - strand)
        # TODO: improve this
        if count % 2 == 0:
            reshaped = numpy.column_stack((x_vals, y_vals))
        else:
            reshaped = numpy.column_stack((x_vals, -y_vals))
            maxtab[:, 1] *= -1

        reshaped = pause_gfx.Filter.repeat_reduction(
            pause_gfx.Filter.minpass(reshaped, min_value=2))

        track_list.append(pause_gfx.Highlight(maxtab))
        track_list.append(pause_gfx.Coverage(reshaped))
        count += 1

    g = pause_gfx.Gfx(track_list)
    data = g.plot()
    with open('out.svg', 'w') as handle:
        handle.write(data)


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
    #if len(sys.argv) <= 1:
        #print "Incorrect arguments"
        #print __doc__
        #sys.exit()
    #kwargs = dict()
    opts = GGO(
        options=[
            ['coverage', 'Coverage files',
             {'multiple': True, 'validate': 'File/Input'}],
            ['starts', 'Start files',
             {'multiple': True, 'validate': 'File/Input'}],
        ],
        outputs=[
        ],
        defaults={
            'appid': 'edu.tamu.cpt.pause2.plotter',
            'appname': 'PAUSE2',
            'appvers': '0.3',
            'appdesc': 'run PAUSE analysis and plotting',
        },
        tests=[],
        doc=__doc__
    )
    options = opts.params()
    main(coverage=options['coverage'],
         starts=options['starts'])


