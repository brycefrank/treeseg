import numpy as np
import geopandas as gpd

class Voronoi:
    def __init__(self, detection_base):
        """

        :param detection_base:
        """

        self.detection_base = detection_base

    @property
    def _centered_coords(self):
        """
        scipy.spatial.Voronoi needs coordinates centered at 0.
        :return:
        """

        array = self.detection_base.height_model.array
        height, width = self.detection_base.height_model.cell_size_x * array.shape[0], \
                        self.detection_base.height_model.cell_size_y * array.shape[1]
        min_x, min_y = self.detection_base.height_model._bounding_box[0], \
                       self.detection_base.height_model._bounding_box[2]

        coords = self.detection_base._coords_array_single
        coords[:, 0], coords[:,1] = coords[:, 0] - (min_x + (width / 2)), coords[:,1] - (min_y + (height / 2))
        return coords

    def translate(self, series):
        """
        Translates the polygons centered at 0 back to physical space.
        :return:
        """

        array = self.detection_base.height_model.array
        height, width = self.detection_base.height_model.cell_size_x * array.shape[0], \
                        self.detection_base.height_model.cell_size_y * array.shape[1]
        min_x, min_y = self.detection_base.height_model._bounding_box[0], \
                       self.detection_base.height_model._bounding_box[2]

        series = series.translate(xoff=min_x + (width / 2), yoff=min_y + (height / 2))
        return series


    def segment(self, intersect=True):
        """
        Segments the input detection object with the Voronoi segmentation algorithm.

        :param intersect: If true, intersects with the bounding box of the height model.
        """
        from scipy.spatial import Voronoi
        from shapely.geometry import LineString
        from shapely.ops import polygonize

        vor = Voronoi(self._centered_coords)
        lines = [LineString(vor.vertices[line]) for line in vor.ridge_vertices if -1 not in line]
        poly_generator = polygonize(lines)

        series = gpd.GeoSeries(poly_generator)
        series = self.translate(series)
        series.crs = self.detection_base.height_model.crs

        if intersect:
            series = series.intersection(self.detection_base.height_model._bounding_box_poly)

        return series



