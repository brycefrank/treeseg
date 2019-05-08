import unittest
import rasterio
import numpy as np
from treeseg import *
from pyproj import Proj
import pyfor
from affine import Affine

rasterio_object = rasterio.open('data/test.tif')
array = rasterio_object.read(1)

class HeightModelTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_hm_array = base.HeightModel(array)
        cls.crs = Proj({'init': 'epsg:26910'}).srs
        cls.pyfor_chm = pyfor.cloud.Cloud('data/test.las').chm(1, interp_method="nearest")

    @classmethod
    def tearDownClass(cls):
        pass

    def test_array_load_no_crs_no_affine(self):
        # Test default behavior
        self.assertEqual(type(self.test_hm_array.array), np.ndarray)
        self.assertIsNone(self.test_hm_array.crs)
        self.assertIsNone(self.test_hm_array.affine)

    def test_array_load_crs_no_affine(self):
        hm = base.HeightModel(array, crs={'init': 'epsg:3007'})
        self.assertEqual(type(hm.array), np.ndarray)
        self.assertIsNone(self.test_hm_array.crs)
        self.assertIsNone(self.test_hm_array.affine)

    def test_pyfor_load_no_crs_no_affine(self):
        hm = base.HeightModel.from_pyfor(self.pyfor_chm)
        self.assertIsNone(hm.crs)
        self.assertIsNone(hm.affine)

    def test_pyfor_load_crs_affine(self):
        self.pyfor_chm.crs = self.crs
        hm = base.HeightModel.from_pyfor(self.pyfor_chm)
        self.assertEqual(type(hm.crs), str)
        self.assertEqual(type(hm.affine), Affine)


