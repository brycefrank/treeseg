from pyproj import Proj

class HeightModel:
    """
    The base class for all rasterized height models used for detection and segmentation.
    """
    def __init__(self, array, crs=None, affine=None):
        self.crs = crs
        if self.crs is not None:
            self._check_crs()

        self.array = array
        self.affine = affine

    def _check_crs(self):
        try:
            Proj(self.crs)
        except RuntimeError:
            import warnings
            warnings.warn('Invalid projection string. Proceeding as usual, but expect errors in georeferenced outputs.')


    @classmethod
    def from_raster(cls, raster_obj):
        pass

    @classmethod
    def from_tif(cls):
        pass

    def plot(self):
        pass

class SegmentBase:
    def __init__(self, height_model):
        pass