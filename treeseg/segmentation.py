from treeseg.base import SegmentBase

class Voronoi:
    def __init__(self, detection_base):
        """

        :param detection_base:
        """

        self.detection_base = detection_base

    def segment(self):
        """
        Segments the input detection object with the Voronoi segmentation algorithm.
        """
        from scipy.spatial import Voronoi, voronoi_plot_2d
        from shapely.geometry import LineString
        from shapely.ops import polygonize

        vor = Voronoi(self.detection_base._coords_array_single, qhull_options="Qbb Qc Qz QJ")

        lines = [LineString(vor.vertices[line]) for line in vor.ridge_vertices if -1 not in line]
        poly_generator = polygonize(lines)

        return SegmentBase(list(poly_generator), self.detection_base.height_model)
