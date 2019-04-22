from treeseg.base import HeightModel, SegmentBase

class Watershed(SegmentBase):
    """
    A wrapper for :func:`skimage.morphology.watershed`.
    """

    def __init__(self, height_model):
        pass

    @property
    def segments(self):
        pass

