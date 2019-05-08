from pyproj import Proj
import numpy as np

class HeightModel:
    """
    The base class for all rasterized height models used for detection and segmentation.
    """
    def __init__(self, array, crs=None, affine=None):
        self.crs = crs
        self.array = array
        self.affine = affine

    @classmethod
    def from_rasterio(cls, rasterio_obj):
        pass

    @classmethod
    def from_tif(cls):
        pass

    @classmethod
    def from_pyfor(cls, pyfor_raster):
        if hasattr(pyfor_raster, 'crs'):
            return cls(pyfor_raster.array, crs = pyfor_raster.crs, affine=pyfor_raster._affine)
        else:
            return cls(pyfor_raster.array, crs=None, affine=None)

    def plot(self):
        pass

class DetectionBase:
    """
    Holding place for a potential base class for detection
    """
    def __init__(self, detected, height_model):
        self.detected = detected
        self.height_model = height_model

    def plot(self):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        caz = ax.matshow(self.height_model.array)
        fig.colorbar(caz)

        container = np.zeros((self.height_model.array.shape[0], self.height_model.array.shape[1], 4))
        container[:, :, 0][self.detected > 0] = 1
        container[:, :, 3][self.detected > 0] = 1

        ax.imshow(container)


class SegmentBase:
    def __init__(self, height_model):
        pass