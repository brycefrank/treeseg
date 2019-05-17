import matplotlib.pyplot as plt
import numpy as np

class HeightModelPlot:
    """
    A base class for managing height model plotting.
    """
    def __init__(self, height_model):
        self.height_model = height_model
        self.fig, self.ax = plt.subplots()

        # Plot the array as background by default.
        self.ax.matshow(height_model.array)

    def append_bool(self, bool_array):
        """
        Appends a boolean array on top of the background array. Usually a boolean array indicates detected tree tops.

        :param bool_array:
        """

        container = np.zeros((bool_array.shape[0], bool_array.shape[1], 4))
        container[:, :, 0][bool_array > 0] = 1
        container[:, :, 3][bool_array > 0] = 1
        self.ax.imshow(container)

    def append_polys(self, polys):
        """
        Appends a list of shapely.geometry.Polygons on top of the background array. Usually, a list of polys indicates
        segmented tree crowns.

        :param polys:
        """
        from descartes import PolygonPatch

        for poly in polys:
            patch = PolygonPatch(poly, facecolor='none', edgecolor='#ffffff', alpha = 1)
            self.ax.add_patch(patch)

