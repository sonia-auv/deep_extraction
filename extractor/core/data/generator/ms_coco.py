import os

import cv2
from PIL import Image
from shapely import wkt
from .abstract.generator import AbstractGenerator


class MSCOCOGenerator(AbstractGenerator):
    SKIPPED_LABEL = 'Skip'

    def __init__(self, logger, file_list):
        super(MSCOCOGenerator, self).__init__(logger)
        self._file_list = file_list

    def _parse_label(self):
        pass

    def _transform_to_format(self, polygon):
        pass

    def _debug_bounding_box(self, xy_coords):
        pass

    def _execute(self):
        pass
