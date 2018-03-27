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
        self._top_border = config['top_border']
        self._bottom_border = config['bottom_border']
        self._left_border = config['left_border']
        self._right_border = config['right_border']
        self._image_ratio = config['image_ratio']
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
        import IPython
        IPython.embed()
        return PascalWriter(
            path=self._image_path,
            width=self._image_width,
            height=self._image_height,
            database=self._project_name)

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
                    y = int(coords['y'])

                xy_coords.extend([x, y])

            label = label.lower()
            self._debug_bounding_box(xy_coords, label)

            self.label_names.add(label)
            xml_writer.addObject(name=label, xy_coords=xy_coords)

        self._check_or_create_annotation_dirs()
        if os.path.exists(self._annotation_file_path):
            xml_writer.save(self._xml_file_path)
            # self._logger.info(
            #    'Pascal VOC annotation file create for image {}.\n\n'.format(self._file_name))
        else:
            self._logger.warning(
                'WARN: Skipping file creation since it already exist at {}\n'.format(self._xml_file_path))

    def _resize_coords(self, x, y):
        horizontal_border_max = max(self._top_border, self._bottom_border)
        vertical_border_max = max(self._left_border, self._right_border)

        new_x = int(x * self._image_ratio)
        new_y = int(y * self._image_ratio)

        return new_x, new_y

    def _debug_bounding_box(self, xy_coords, label):
        image = cv2.imread(self._image_path)

        value = 4

        top_left = [xy_coords[0] - value, xy_coords[1] - value]
        bottom_left = [xy_coords[2] - value, xy_coords[3] + value]
        top_right = [xy_coords[4] + value, xy_coords[5] - value]
        bottom_right = [xy_coords[6] + value, xy_coords[7] + value]

        top_xy = tuple(top_left)
        bottom_xy = tuple(bottom_right)

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
