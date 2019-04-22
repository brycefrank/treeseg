import unittest
import rasterio
import numpy as np
from treeseg import *

rasterio_object = rasterio.open('data/test.tif')


# TODO consider only using arrays, crs, and affine as needed arguments
class RasterBaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_rb = base.RasterBase(rasterio_object)

    def test_obj_load(self):
        self.assertEqual(type(self.test_rb.array), np.ndarray)

    def test_array_load(self):
        test_rb_array = base.RasterBase.from_array(rasterio_object.read(1))
        self.assertEqual(type(test_rb_array.array), np.ndarray)


class DetectedTopsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_d = detection.DetectedTops(rasterio_object)
        test_d = detection.DetectedTops.from_array(rasterio_object.read(1))