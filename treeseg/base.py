from rasterio.io import MemoryFile

class RasterBase:
    def __init__(self, raster_obj):
        self.array = raster_obj.read(1)

    @classmethod
    def from_array(cls, array):
        with MemoryFile().open(driver='GTiff', count=1, height=array.shape[0], width=array.shape[1]) as memfile:
            memfile.write(array, 1)

            return cls(memfile)
