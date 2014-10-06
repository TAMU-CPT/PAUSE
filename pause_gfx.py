#!/usr/bin/env python
"""PAUSE graphics backend

Library only (for now)
"""

import svgwrite
import numpy

class Track(object):

    def __init__(self, data):
        self.data = numpy.array(data)
        self.dmax = numpy.max(self.data[:, 1])
        self.dmin = numpy.min(self.data[:, 1])
        self.amax = numpy.max(numpy.abs(self.data[:, 1]))
        self.length = numpy.max(data[:, 0])
        # Invert data for SVG (This is because 0 is top, 1000 is bottom, so
        # when we add +200 to move downwards, we need to substract X to move
        # back up)
        self.data[:, 1] = self.data[:, 1] * -1


class Coverage(Track):

    def __init__(self, data, line_width=1, line_color='black', fill='grey'):
        Track.__init__(self, data)
        self.style = {
            'line_width': line_width,
            'line_color': line_color,
            'fill': fill
        }

    def plot(self, svg, points):
        return [svg.polygon(points, stroke_width=self.style['line_width'],
                            stroke=self.style['line_color'],
                            fill=self.style['fill'])]


class Highlight(Track):

    def __init__(self, data, line_width=1, line_color='red', fill='none'):
        Track.__init__(self, data)
        self.style = {
            'line_width': line_width,
            'line_color': line_color,
            'fill': fill
        }

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
        dataset_max = numpy.max([f.amax for f in self.tracks])
        # Scale = Number of KB per row
        number_of_rows = dataset_length / scale / 1000
        points_per_row = scale * 1000
        # Scaling Factors
        row_x_scaling_factor = float(points_per_row) / float(width)
        row_y_scaling_factor = float(self.row_height) / float(2 * dataset_max)

        svg = svgwrite.Drawing(size=("%spx" % width,
                                     "%spx" % (number_of_rows *
                                               self.row_height)))

        for track in self.tracks:
            for subset_idx in range(number_of_rows):
                # Subset our data
                start = subset_idx * points_per_row
                end = (1 + subset_idx) * points_per_row
                # Only points in this row
                subset = [start, 0]
                subset += [p for p in track.data if start <= p[0] <= end]
                subset += [end, 0]

                print subset
                if len(subset) > 0:
                    x_subset = subset[:, 0]
                    y_subset = subset[:, 1]
                    # Offset the data for Y
                    row_y_offset = self.row_height * subset_idx
                    # Apply data reshaping
                    row_y_values = (y_subset * row_y_scaling_factor) + row_y_offset
                    row_x_values = (x_subset / row_x_scaling_factor) - (subset_idx * width)
                    # Restack data into [[], []]
                    reshaped = numpy.column_stack((row_x_values, row_y_values))
                    ##http://stackoverflow.com/a/10016379
                    points = tuple(map(tuple, reshaped))
                    for dataset in track.plot(svg, points):
                        svg.add(dataset)

        return svg.tostring()


class Filter(object):

    def __init__(self):
        pass

    @classmethod
    def downsample(cls, data):
        """
            Need a method to downsample data. Given a range that looks like

            [[14300    3]
             [14301    0]
             [14302    0]
             [14303    0]
             [14304    0]
             [14305    4]]

            this method will downsample the data and removing ranges of
            "useless" points, and return data like:

            [[14300    3]
             [14301    0]
             [14304    0]
             [14305    4]]

            note the missing range of zeros, but the bounding zeros left in.
            Should not be specific to 0.
        """
        fixed = []
        # start out with first element
        fixed.append(data[0])
        # Last thing we added was y value
        #last_added = data[0][1]
        for i in range(1, len(data)-1):
            prev = data[i-1][1]
            curr = data[i][1]
            nexe = data[i+1][1]
            # If the value is the same as the previos and the next, we ignore it completely
            if prev == curr and curr == nexe:
                pass
            # Otherwise, we add it to the stack
            else:
                fixed.append(data[i])
        return numpy.array(fixed)

    @classmethod
    def minpass(cls, data, min_value=5):
        """
            Zero out y values lower than a bound X. Should probably be set to a
            % of max_value

            TODO: more efficient implementation
        """
        fixed = []
        for row in data:
            if row[1] >= min_value:
                fixed.append(row)
            else:
                fixed.append([row[0], 0])
        return numpy.array(fixed)
