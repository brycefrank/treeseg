import unittest
import rasterio
import numpy as np
from treeseg import *
from pyproj import Proj

rasterio_object = rasterio.open('data/test.tif')
array = rasterio_object.read(1)

# TODO consider only using arrays, crs, and affine as needed arguments
class HeightModelTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_hm_array = base.HeightModel(array)

    def test_array_load_no_crs_no_affine(self):
        # Test default behavior
        self.assertEqual(type(self.test_hm_array.array), np.ndarray)
        self.assertIsNone(self.test_hm_array.crs)
        self.assertIsNone(self.test_hm_array.affine)

    def test_array_load_bad_projection(self):
        self.assertWarns(UserWarning, base.HeightModel, (array), {'crs': {'init': 'epsg:3007asdf'}})

    def test_array_load_crs_no_affine(self):
        base.HeightModel(array, crs={'init': 'epsg:3007'})
        self.assertEqual(type(self.test_hm_array.array), np.ndarray)
        self.assertIsNone(self.test_hm_array.crs)
        self.assertIsNone(self.test_hm_array.affine)


    def test_obj_load(self):
        self.assertEqual(type(self.test_hm_array.array), np.ndarray)
