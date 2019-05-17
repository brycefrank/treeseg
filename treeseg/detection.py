import numpy as np
from treeseg.base import DetectionBase

class LocalMaximaBase:
    """
    Base class for local maxima filters. All derivatives use ``skimage.feature.peak_local_max``, and this base class
    handles a transformation of inputs from the user (e.g. in meters) into pixels.
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
        Rounds down to the nearest unit of measurement.

        :param affine: An affine transformation.
        :return: An integer representing the number of pixels considered for minimum distance.
        """

        return int(np.floor(self.min_distance / affine[0]))

    def _get_pixel_min_dist(self, height_model):
        if hasattr(height_model, 'affine'):
            pixel_min_dist = self._convert_min_dist(height_model.affine)
        else:
            pixel_min_dist = self.min_distance
        return pixel_min_dist


class FixedWindowLocalMaxima(LocalMaximaBase):
    """
    Implements a local maxima detection filter via ``skimage.feature.peak_local_max``.
    """

    def detect(self, height_model):
        from skimage.feature import peak_local_max
        detect_array = peak_local_max(height_model.array, min_distance=self._get_pixel_min_dist,
                                      threshold_abs=self.threshold_abs, exclude_border=self.exclude_border,
                                      num_peaks=self.num_peaks, indices=False)

        return DetectionBase(detect_array, height_model)

class VariableWindowLocalMaxima(LocalMaximaBase):
    """
    Implements a variable window local maxima. This first runs a fixed window local maxima. Then it iterates over all
    of the detections from that filter. In each variable window, the tallest maxima is retained, and the others are
    discarded.

    By default this function uses the coefficients described in Popescu et al. (2002), but this can be replaced by any
    arbitrary allometric equation by setting the ``.variable_window_function`` attribute. The function must take a single
    argument, the height of any given pixel in the units of the input height model (e.g. meters).
    """

    def __init__(self, a=2.21, b=0.01022, **kwargs):
        super(VariableWindowLocalMaxima, self).__init__(**kwargs)
        self.variable_window_function = lambda height: a + b * height **2

    def _units_to_pixel_bounds(self, units, resolution, i, j):
        """
        Converts an allometric window position within the height model from physical units (e.g. meters) to array space.
        :param units: The number of physical space units to convert.
        :param resolution: The resolution of the height model.
        :param i: The row position of the height model.
        :param j: The col position of the height model.
        :return: A tuple that contains two tuples describing the bounding box of the window in array space.
        """

        diff = int(np.ceil(units / resolution) // 2)
        lb_i, ub_i = i - diff, i + diff
        lb_j, ub_j = j - diff, j + diff
        return ((lb_i, ub_i), (lb_j, ub_j))

    @property
    def variable_window_function(self):
        return self.__variable_window_function

    @variable_window_function.setter
    def variable_window_function(self, func):
        self.__variable_window_function = func

    def _get_window(self, array, resolution, i, j):
        """
        :param array: Some input array
        :param resolution: The resolution of the height model in physical space.
        :param i: The row position.
        :param j: The column position.
        :return: A tuple. The first element is the window array, and the second and third elements are the left and top
        positions in array space.
        """
        window_width = self.variable_window_function(array[i, j])
        bounds = self._units_to_pixel_bounds(window_width, resolution, i, j)
        mat = array[bounds[0][0]:bounds[0][1], bounds[1][0]:bounds[1][1]]
        return mat, bounds[0][0], bounds[1][0]

    def _get_window_poly(self, bbox):
        from shapely.geometry import Polygon
        return Polygon(((bbox[0], bbox[1]), (bbox[0], bbox[3]), (bbox[2], bbox[3]), (bbox[2], bbox[1])))

    def _diagnostic_plot(self, polys, height_model, detected):
        """
        Plots the variable windows as geometries in the canopy height model.
        """
        import matplotlib.pyplot as plt
        from descartes import PolygonPatch

        fig, ax = plt.subplots()
        ax.matshow(height_model.array)

        # TODO REMOVE
        container = np.zeros((height_model.array.shape[0], height_model.array.shape[1], 4))
        container[:, :, 0][detected > 0] = 1
        container[:, :, 3][detected > 0] = 1
        ax.imshow(container)

        for poly in polys:
            patch = PolygonPatch(poly, facecolor='#cccccc', edgecolor='#999999', alpha = 1)
            patch.set_facecolor('none')
            ax.add_patch(patch)


    def _get_high_intensity_peaks(self, image, mask, num_peaks):
        """
        Return the highest intensity peak coordinates.
        """
        # get coordinates of peaks
        coord = np.nonzero(mask)
        intensities = image[coord]
        idx_maxsort = np.argsort(intensities)
        print(idx_maxsort)
        # select num_peaks peaks
        if len(coord[0]) > num_peaks:
            coord = np.transpose(coord)[idx_maxsort][-num_peaks:]
        else:
            coord = np.column_stack(coord)[idx_maxsort]
        # Highest peak first

        return coord[::-1]

    def detect(self, height_model, diagnostic=False):
        from scipy.ndimage.filters import maximum_filter

        array = height_model.array
        max_array = maximum_filter(array, size= 2 * self.min_distance + 1, mode='constant')
        mask = array == max_array

        if self.threshold_abs is not None:
            mask &= array > self.threshold_abs
        peaks = self._get_high_intensity_peaks(array, mask, num_peaks=np.inf)

        max_rows, max_cols = [], []
        polys = []

        for peak in peaks:
            row, col = peak
            height_window, left, top = self._get_window(array, height_model.cell_size_x, row, col)

            if height_window.size > 0:
                # Get the relative index of the highest point in this array
                rel_max_inds = np.where(height_window == np.max(height_window))

                # Are we considering the same index? That is, is the pixel found above the same as the one we
                # are iterating on?
                abs_max_rows = rel_max_inds[0] + left
                abs_max_cols = rel_max_inds[1] + top

                for i in zip(abs_max_rows, abs_max_cols):
                    if (row, col) == i: # Then this guy is a maximum in this variable window! append!
                        max_rows.append(row)
                        max_cols.append(col)

                        if diagnostic:
                            bbox = top, left, height_window.shape[1] + top, height_window.shape[0] + left
                            polys.append(self._get_window_poly(bbox))

        detected = np.zeros(array.shape)
        detected[max_rows, max_cols] = 1
        self._diagnostic_plot(polys, height_model, detected)
        return DetectionBase(detected, height_model)

