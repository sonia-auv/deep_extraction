import os
import cv2
from PIL import Image
from pascal_voc_writer import Writer as PascalWriter

from .abstract.generator import AbstractGenerator


class PascalVOCGenerator(AbstractGenerator):
    SKIPPED_LABEL = 'Skip'

    def __init__(self, logger, config):
        super(PascalVOCGenerator, self).__init__(logger)
        self._labelbox_id = config['labelbox_id']
        self._project_name = config['project_name']
        self._json_labels = config['json_labels']
        self._annotation_dir = config['annotation_dir']
        self._image_path = config['image_path']
        self._image_width = config['image_width']
        self._image_height = config['image_height']
        self._x_factor = config['x_factor']
        self._y_factor = config['y_factor']
        self._pad_top = config['pad_top']
        self._pad_left = config['pad_left']
        self._apply_reduction = config['apply_reduction']
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

    def _transform_to_format(self):
        pass

    def _parse_label(self):
        """ Parse labels and extract. """
        xml_writer = self._create_pascal_writer()

        for label, bnd_box in self._json_labels.items():
            bnd_box = bnd_box[0]
            xy_coords = []

            for coords in bnd_box:
                if self._apply_reduction:
                    x, y = self._resize_coords(coords['x'], coords['y'])
                else:
                    x = int(coords['x'])
                    y = self._image_height - int(coords['y'])

                xy_coords.extend([x, y])

            label = label.lower()
            self._debug_bounding_box(xy_coords, label)

            self.label_names.add(label)
            xml_writer.addObject(name=label, xy_coords=xy_coords)

        self._check_or_create_annotation_dirs()
        if os.path.exists(self._annotation_file_path):
            xml_writer.save(self._xml_file_path)
            # self._logger.info(
            #     'Pascal VOC annotation file create for image {}.\n\n'.format(self._file_name))
        else:
            self._logger.warning(
                'WARN: Skipping file creation since it already exist at {}\n'.format(self._xml_file_path))

    def _resize_coords(self, x, y):

        new_x = int(x / self._x_factor)
        new_y = self._image_height - int(y / self._y_factor) - self._pad_top
        return new_x, new_y

    def _debug_bounding_box(self, xy_coords, label):
        image = cv2.imread(self._image_path)

        value = 0

        top_xy = tuple([xy_coords[0] - value, xy_coords[1] - value])
        bottom_xy = tuple([xy_coords[4] + value, xy_coords[5] + value])

        img = cv2.rectangle(image, top_xy, bottom_xy, (0, 255, 0), 1)

        base_name = os.path.basename(self._image_path)
        file_name = os.path.join('/home/spark/Desktop/test/', base_name)
       # cv2.imshow('Bounding box', image)
        cv2.imwrite(file_name, img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

    def _execute(self):
        """ Execute JSON to Pascal VOC conversion. """
        if self._json_labels != self.SKIPPED_LABEL:
            self._logger.info(
                'Transforming shapely wtk polygon format to pascal voc.\n')
            self._parse_label()
        else:
            self._logger.warning(
                'WARN:Skipping annotation since images has been skipped at labeling time')
