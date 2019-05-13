from pyproj import Proj
import geopandas as gpd
from shapely.geometry import Point, Polygon
import numpy as np
import rasterio

class HeightModel:
    """
    The base class for all rasterized height models used for detection and segmentation.
    """
    def __init__(self, array, crs=None, affine=None):
        self.crs = crs
        self.array = array
        self.affine = affine

        self.cell_size_x = self.affine[0]
        self.cell_size_y = abs(self.affine[4])

    @classmethod
    def from_rasterio(cls, rasterio_obj):
        pass

    @classmethod
    def from_tif(cls, tif_path):
        with rasterio.open(tif_path, 'r') as rast:
            return cls(rast.read(1), crs=rast.crs, affine=rast.transform)

    @classmethod
    def from_pyfor(cls, pyfor_raster):
        if hasattr(pyfor_raster, 'crs'):
            return cls(pyfor_raster.array, crs = pyfor_raster.crs, affine=pyfor_raster._affine)
        else:
            return cls(pyfor_raster.array, crs=None, affine=None)

    @property
    def _bounding_box(self):
        min_x, max_y = self.affine[2], self.affine[5]
        max_x, min_y = min_x + self.cell_size_x * self.array.shape[1], max_y - self.cell_size_y * self.array.shape[0]
        return(min_x, max_x, min_y, max_y)

    @property
    def _bounding_box_poly(self):
        min_x, max_x, min_y, max_y = self._bounding_box
        return Polygon([[min_x, min_y], [min_x, max_y], [max_x, max_y], [max_x, min_y]])


    def plot(self):
        pass

class DetectionBase:
    """
    Holding place for a potential base class for detection
    """
    def __init__(self, detected, height_model):
        self.detected = detected
        self.height_model = height_model

    def project_indices(self, indices):
        max_y = self.height_model._bounding_box[3]
        min_x = self.height_model._bounding_box[0]

        seed_xy = indices[:, 1] * self.height_model.cell_size_x + min_x, max_y - (indices[:,0] * self.height_model.cell_size_y)
        seed_xy = np.stack(seed_xy, axis = 1)
        seed_xy[:, 0], seed_xy[:,1] = seed_xy[:, 0] + (self.height_model.cell_size_x / 2), seed_xy[:,1] - (self.height_model.cell_size_y / 2)

        return seed_xy

    @property
    def _indices_single(self):
        """
        :return: A boolean array of detected tops for the height model.
        """
        from scipy.ndimage.measurements import center_of_mass, label
        labels = label(self.detected)[0]
        centers = center_of_mass(self.detected, labels, range(1, np.max(labels)+1))
        centers = np.array(centers)
        return centers

    @property
    def _coords_array_single(self):
        return self.project_indices(self._indices_single)

    @property
    def _coords_array_multiple(self):
        indices = np.stack(np.where(self.detected), axis=1)
        return self.project_indices(indices)

    @property
    def points(self, single=True):
        """
        Returns a GeoSeries of point geometries.
        """
        if single:
            coords = self._coords_array_single
        else:
            coords = self._coords_array_multiple

        series = gpd.GeoSeries([Point(xy) for xy in coords])
        series.crs = self.height_model.crs
        return series

    def plot(self):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        caz = ax.matshow(self.height_model.array)
        fig.colorbar(caz)

        container = np.zeros((self.height_model.array.shape[0], self.height_model.array.shape[1], 4))
        container[:, :, 0][self.detected > 0] = 1
        container[:, :, 3][self.detected > 0] = 1

        ax.imshow(container)



