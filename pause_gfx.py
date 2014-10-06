#!/usr/bin/env python
"""PAUSE graphics backend

Library only (for now)
"""

import svgwrite
import numpy


class Track(object):

    def __init__(self, data, line_width=1, line_color='black', fill='gray'):
        self.data = numpy.array(data)
        self.style = {
            'line_width': line_width,
            'line_color': line_color,
            'fill': fill
        }
        self.dmax = numpy.max(self.data[:,1])
        self.dmin = numpy.min(self.data[:,1])
        self.length = len(data[:,1])
        # Invert data for SVG
        self.data[:,1] = self.data[:,1] * -1


    def plot(self, svg, points):
        return [svg.polygon(points, stroke_width=self.style['line_width'],
                            stroke=self.style['line_color'],
                            fill=self.style['fill'])]


class Highlight(object):

    def __init__(self, data, line_width=2, line_color='red', fill='none'):
        self.data = numpy.array(data)
        self.style = {
            'line_width': line_width,
            'line_color': line_color,
            'fill': fill
        }
        self.dmax = numpy.max(self.data)
        self.dmin = numpy.min(self.data)
        self.length = len(data)

    def plot(self, svg, points):
        data = []
        for point in points:
            data.append(svg.circle(center=point, r=15,
                                   stroke_width=self.style['line_width'],
                                   stroke=self.style['line_color'],
                                   fill=self.style['fill']))
        return data


class Gfx(object):

    def __init__(self, tracks=None):
        if tracks is None:
            self.tracks = []
        else:
            self.tracks = tracks
        self.row_height = 200

    def add_track(self, data):
        self.tracks.append(data)

    def plot(self, width=1000, scale=5):
        dataset_length = numpy.max([f.length for f in self.tracks])
        dataset_max = numpy.max([f.dmax for f in self.tracks])
        # Scale = Number of KB per row
        number_of_rows = dataset_length / scale / 1000
        points_per_row = scale * 1000
        # Scaling Factors
        row_x_scaling_factor = float(points_per_row) / float(width)
        row_y_scaling_factor = float(self.row_height) / float(2 * dataset_max)

        svg = svgwrite.Drawing(size=("%spx" % width,
                                     "%spx" % (number_of_rows *
                                               self.row_height)))

        for track in [track for track in self.tracks
                      if isinstance(track, Track)]:
            for subset_idx in range(number_of_rows):
                # Subset our data
                start = subset_idx * points_per_row
                end = (1 + subset_idx) * points_per_row
                x_subset = track.data[:,0][start:end]
                y_subset = track.data[:,1][start:end]
                # Offset the data for Y
                row_y_offset = self.row_height * subset_idx

                row_y_values = (y_subset * row_y_scaling_factor) + row_y_offset
                row_x_values = x_subset / row_x_scaling_factor

                reshaped = numpy.column_stack((row_x_values, row_y_values))
                ##http://stackoverflow.com/a/10016379
                points = tuple(map(tuple, reshaped))
                for dataset in track.plot(svg, points):
                    svg.add(dataset)

        #for highlight in [track for track in self.tracks
                          #if isinstance(track, Highlight)]:
            #for subset_idx in range(number_of_rows):
                #start = subset_idx * points_per_row
                #end = (1 + subset_idx) * points_per_row
                #points = numpy.array([p for p in highlight.data if start <= p[0] <= end])
                #if len(points) > 0:
                    ## Offset the data for Y
                    #row_y_offset = self.row_height * subset_idx

                    #row_x_values = (-points[:, 1] * row_y_scaling_factor) + row_y_offset
                    #row_y_values = points[:, 0] / row_x_scaling_factor

                    #reshaped = numpy.column_stack((row_x_values, row_y_values))
                    ###http://stackoverflow.com/a/10016379
                    #points = tuple(map(tuple, reshaped))
                    #for point in points:
                        #svg.add(svg.circle(center=point, r=15,
                                           #stroke_width=track.style['line_width'],
                                           #stroke=track.style['line_color'],
                                           #fill=track.style['fill']))

        return svg.tostring()
