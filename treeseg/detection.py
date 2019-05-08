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

        return self.min_distance / affine[0]

    def detect(self, height_model):
        from skimage.feature import peak_local_max

        if hasattr(height_model, 'affine'):
            pixel_min_dist = self._convert_min_dist(height_model.affine)
        else:
            pixel_min_dist = self.min_distance

        detect_array = peak_local_max(height_model.array, min_distance=self.min_distance, threshold_abs=self.threshold_abs,
                       exclude_border=self.exclude_border, num_peaks=self.num_peaks, indices=False)

        return DetectionBase(detect_array, height_model)



