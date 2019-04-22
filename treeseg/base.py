from pyproj import Proj

class HeightModel:
    """
    The base class for all rasterized height models used for detection and segmentation.
    """

    def __init__(self, array, crs=None, affine=None):
        try:
            Proj(crs)
        except RuntimeError:
            import warnings
            warnings.warn('Invalid projection string. Proceeding as usual, but expect errors in georeferenced outputs.')

        self.array = array
        self.crs = crs
        self.affine = affine

    @classmethod
    def from_raster(cls, raster_obj):
        pass

    @classmethod
    def from_tif(cls):
        pass

class SegmentBase:
    def __init__(self, height_model):
        pass