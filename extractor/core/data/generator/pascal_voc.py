import os

import cv2
from PIL import Image
from shapely import wkt

from pascal_voc_writer import Writer as PascalWriter

from .abstract.generator import AbstractGenerator


class PascalVOCGenerator(AbstractGenerator):
    SKIPPED_LABEL = 'Skip'

    def __init__(self, logger, config):
        self._logger = logger(__name__)
        self._labelbox_id = config['labelbox_id']
        self._project_name = config['project_name']
        self._json_labels = config['json_labels']
        self._annotation_dir = config['annotation_dir']
        self._image_path = config['image_path']
        self._image_width = config['image_width']
        self._image_height = config['image_height']
        self._top_border = config['top_border']
        self._bottom_border = config['bottom_border']
        self._left_border = config['left_border']
        self._right_border = config['right_border']
        self._image_ratio = config['image_ratio']
        self._apply_reduction = config['apply_reduction']
        self._debug = config['debug']

        self.label_names = set()

        self._execute()

    @property
    def _xml_file_name(self):
        """ Generate xml filename and ext. """
        file_name = os.path.splitext(os.path.basename(self._image_path))[0]
        return '{}.xml'.format(file_name)

    @property
    def _xml_file_path(self):
        """ Generate xml file path. """
        return os.path.join(self._annotation_file_path, self._xml_file_name)

    @property
    def _annotation_file_path(self):
        """ Generate annotation pascal voc folder path. """
        return os.path.join(self._annotation_dir, 'pascal_voc')

    def _check_or_create_annotation_dirs(self):
        """ Check folder exist or create. """
        if not os.path.exists(self._annotation_file_path):
            os.makedirs(self._annotation_file_path)

    def _create_pascal_writer(self):
        """ Create an instance of pascal writer."""
        return PascalWriter(
            path=self._image_path,
            width=self._image_width,
            height=self._image_height,
            database=self._project_name)

    def _parse_label(self):
        """ Parse labels and extract WKT polygons."""
        xml_writer = self._create_pascal_writer()

        for label, polygon in self._json_labels.items():
            try:
                poly = wkt.loads(polygon)

                xy_coords = self._transform_to_format(poly)

                self.label_names.add(label.lower())
                xml_writer.addObject(name=label.lower(), xy_coords=xy_coords)

            except:
                self._logger.exception(
                    'EXCEPT: Label {} polygon points count is less than four'.format(self._labelbox_id))

        self._check_or_create_annotation_dirs()

        if os.path.exists(self._annotation_file_path):
            xml_writer.save(self._xml_file_path)
            # self._logger.info(
            #    'Pascal VOC annotation file create for image {}.\n\n'.format(self._file_name))
        else:
            self._logger.warning(
                'WARN: Skipping file creation since it already exist at {}\n'.format(self._xml_file_path))

    def _transform_to_format(self, polygon):
        """ Trandform WKT polygon to Pascal VOC format. """
        for poly in polygon:
            xy_coords = []
            for x, y in poly.exterior.coords:
                horizontal_border_max = max(self._top_border, self._bottom_border)
                vertical_border_max = max(self._left_border, self._right_border)

                if self._apply_reduction:
                    new_x = int(x*self._image_ratio)
                    new_y = int(y*self._image_ratio)

                    if horizontal_border_max > vertical_border_max:
                        new_y = self._image_height - new_y - self._bottom_border
                    else:
                        new_x = self._image_width - new_x - self._right_border

                    xy_coords.extend([new_x, new_y])
                else:
                    new_x = x
                    new_y = y

                    if horizontal_border_max > vertical_border_max:
                        new_y = self._image_height-new_y
                    else:
                        new_x = self._image_width - x

                    xy_coords.extend([new_x, new_y])

            # remove last polygon if it is identical to first point
            if xy_coords[-2:] == xy_coords[:2]:
                xy_coords = xy_coords[:-2]

            if self._debug:
                self._debug_bounding_box(xy_coords)

        return xy_coords

    def _debug_bounding_box(self, xy_coords):
        """ Display image and bounding box to opencv window."""
        image = cv2.imread(self._image_path)

        top_xy = (xy_coords[2], xy_coords[3])
        bottom_xy = (xy_coords[6], xy_coords[7])

        cv2.rectangle(image, top_xy, bottom_xy, (0, 255, 0), 1)
        cv2.imshow('Bounding box', image)
        cv2.waitKey(1000)
        cv2.destroyAllWindows()

    def _execute(self):
        """ Execute JSON to Pascal VOC conversion. """
        if self._json_labels != self.SKIPPED_LABEL:
            self._logger.info(
                'Transforming shapely wtk polygon format to pascal voc.\n')
            self._parse_label()
        else:
            self._logger.warning(
                'WARN:Skipping annotation since images has been skipped at labeling time')
