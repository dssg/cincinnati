import numpy as np


def configure_split(column_sizes):
    """
    In several datafiles there is no separator between columns, they are simply concatenated to each other.
    Information on where to split the columns is usually given in a pdf file that contains column sizes.
    This function takes a list of columns sizes and configures a splitting function.
    :param column_sizes: list of column sizes
    :return reference to splitting function
    """
    column_starts = np.cumsum([0]+list(column_sizes))[:-1]
    column_stops = np.cumsum(list(column_sizes))

    def perform_split(line):
        """
        Split a line at the previously configured column starts and stops.
        """
        return [line[start:stop].strip()
                for start, stop in zip(column_starts, column_stops)]

    return perform_split