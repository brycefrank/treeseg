import numpy as np
from treeseg.base import DetectionBase

class FixedWindowLocalMaxima:
    """
    Implements a local maxima detection filter via ``skimage.feature.peak_local_max``.
    """

    def __init__(self, min_distance=1, threshold_abs=None, exclude_border=True, num_peaks=np.inf):
        """
        This is not a strict wrapper for ``peak_local_max`` and is designed specifically to handle the spatial
        referencing. See ``peak_local_max`` documentation for particulars.
        :param min_distance: The minimum distance between maxima in the same units of distance as the coordinate system.
        :param threshold_abs: Minimum intensity of maxima.
        :param exclude_border: Excludes maxima found at the distance specified as an integer to this argument, in the units of the coordinate system.
        :param num_peaks: The maximum number of maxima to return.
        """

        self.min_distance = min_distance
        self.threshold_abs = threshold_abs
        self.exclude_border = exclude_border
        self.num_peaks = num_peaks

    def _convert_min_dist(self, affine):
        """
        ``peak_local_max`` requires this distance defined as a number of pixels, rather than any physical coordinate
        system. This function translates the user input (in, presumably, a real coordinate system) to pixel coordinates.

        :return: An integer representing the number of pixels considered for minimum distance.
        """

        return int(np.floor(self.min_distance / affine[0]))

    def detect(self, height_model):
        from skimage.feature import peak_local_max

        if hasattr(height_model, 'affine'):
            pixel_min_dist = self._convert_min_dist(height_model.affine)
        else:
            pixel_min_dist = self.min_distance

        detect_array = peak_local_max(height_model.array, min_distance=pixel_min_dist, threshold_abs=self.threshold_abs,
                       exclude_border=self.exclude_border, num_peaks=self.num_peaks, indices=False)


        return DetectionBase(detect_array, height_model)

class VariableWindowLocalMaxima:
    """
    Implements a variable window local maxima in the style of Popescu et al. (2002).
    """

    def __init__(self, min_distance=1, threshold_abs = 2):
        self.threshold_abs = threshold_abs
        self.min_distance = min_distance

    def _meters_to_pixel_bounds(self, meters, resolution, i, j):
        diff = int(np.ceil(meters / resolution) // 2)
        lb_i, ub_i = i - diff, i + diff
        lb_j, ub_j = j - diff, j + diff
        return ((lb_i, ub_i), (lb_j, ub_j))

    def _window_width_meters(self, height, a=2.21, b=0.01022):
        return a + b * height**2

    def _get_window(self, array, resolution, i, j):
        window_width = self._window_width_meters(array[i, j], a=1.21, b=0.005)
        bounds = self._meters_to_pixel_bounds(window_width, resolution, i, j)
        mat = array[bounds[0][0]:bounds[0][1], bounds[1][0]:bounds[1][1]]
        return mat, bounds[0][0], bounds[1][0]

    def _get_high_intensity_peaks(self, image, mask, num_peaks):
        """
        Return the highest intensity peak coordinates.
        """
        # get coordinates of peaks
        coord = np.nonzero(mask)
        # select num_peaks peaks
        if len(coord[0]) > num_peaks:
            intensities = image[coord]
            print(intensities)
            idx_maxsort = np.argsort(intensities)
            coord = np.transpose(coord)[idx_maxsort][-num_peaks:]
        else:
            coord = np.column_stack(coord)
        # Highest peak first
        return coord[::-1]

    def detect(self, height_model):
        from matplotlib import pyplot as plt
        from scipy.ndimage.filters import maximum_filter

        array = height_model.array
        max_array = maximum_filter(array, size=2 *self.min_distance + 1, mode='constant')

        mask = array == max_array
        mask &= array > self.threshold_abs

        peaks = self._get_high_intensity_peaks(array, mask, num_peaks=np.inf)


        max_rows, max_cols = [], []
        for peak in peaks:
            row, col = peak

            peak_height = array[row,col]

            tree_mat, left, top = self._get_window(array, height_model.cell_size_x, row, col)

            if tree_mat.size > 0:
                # Get the relative coordinates
                maxes = np.where(tree_mat == np.max(tree_mat))

                # Handle negative bounds:
                if top < 0:
                    top = 0
                if left < 0:
                    left = 0

                # Move relative coordinates to true array position
                max_rows.append(maxes[0] + left)
                max_cols.append(maxes[1] + top)

        max_rows = np.concatenate(max_rows)
        max_cols = np.concatenate(max_cols)


        detected = np.zeros(array.shape)

        detected[max_rows, max_cols] = 1
        plt.matshow(mask)
        #plt.matshow(detected)
        #plt.show()
        return DetectionBase(detected, height_model)







def fold():
    for i in range(0, array.shape[0]):
        for j in range(0, array.shape[1]):
            mat = self._get_window(array, height_model.cell_size_x, i, j)
            mat[mat < self.threshold_abs] = 0
            if mat.size > 0:
                maxes = np.where(np.max(mat) == mat)
                row, col = maxes[0] + i, maxes[1] + j

                if any(row >= array.shape[0]) or any(col >= array.shape[1]):
                    pass
                else:
                    max_rows.append(row)
                    max_cols.append(col)

    max_rows = np.concatenate(max_rows)
    max_cols = np.concatenate(max_cols)


    detect_array = np.zeros(array.shape)
    detect_array[max_rows, max_cols] = 1
    peaks = self._get_high_intensity_peaks(array, detect_array, 1000)

    detect_array = np.zeros(array.shape)
    detect_array[peaks[:,0], peaks[:,1]] = 1

    return DetectionBase(detect_array, height_model)
