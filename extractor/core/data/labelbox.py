import Augmentor
import os
import json
import requests
import cv2
import datetime as dt
import numpy as np
from PIL import Image
from shapely import wkt
from pascal_voc_writer import Writer as PascalWriter

from .generator.pascal_voc import PascalVOCGenerator
from .generator.ms_coco import MSCOCOGenerator


class LabeledImagesMSCOCO:
    """ Custom class matching returned json object of labelbox.io. """

    def __init__(self, logger, *args, **kwargs):
        self._logger = logger(__name__)
        self._json_data = kwargs['json_data']
        self._image_dir = kwargs['image_dir']
        self._resized_image_dir = kwargs['resized_image_dir']
        self._annotations_dir = kwargs['annotations_dir']
        self._required_img_width = kwargs['required_image_width']
        self._required_img_height = kwargs['required_image_height']
        # TODO:Complete refactor


class LabeledImagePascalVOC:
    """ Custom class matching returned json object of labelbox.io. """

    ANNOTATION_PASCAL_VOC = 'Pascal VOC'
    ANNOTATION_COCO = 'COCO'
    SKIPPED_LABEL = 'Skip'

    def __init__(self, logger, *args, **kwargs):
        self._logger = logger(__name__)
        self._id = kwargs['ID']
        self._source_img_url = kwargs['Labeled Data']
        self._created_by = kwargs['Created By']
        self._project_name = kwargs['Project Name']
        self._seconds_to_label = kwargs['Seconds to Label']
        self._images_dir = kwargs['Images Dir']
        self._resized_image_dir = kwargs['Resized Image Dir']
        self._annotations_dir = kwargs['Annotations Dir']
        self._required_img_height = kwargs['Required Image Height']
        self._required_img_width = kwargs['Required Image Width']
        self._annotation_type = kwargs['Annotation Type']
        self.label_names = set()
        self._file_name = self._source_img_url.rsplit('/', 1)[-1].split('.')[0]
        self._file_ext = '.' + \
            self._source_img_url.split("/")[-1].split('.')[1]
        self._downloaded_images = []
        self._resized_images = []
        self._download_image(kwargs['Label'])
        self._resize_image(self._image_file_path)
        self._generate_annotations(logger, kwargs['Label'])

    def _download_image(self, json_labels):
        """ Download image from provided link (Cloud link)."""
        file_name = self._file_name + self._file_ext
        self._image_file_path = os.path.join(self._images_dir, file_name)

        if not os.path.exists(self._image_file_path):
            try:
                response = requests.get(self._source_img_url, stream=True)
                response.raw.decode_content = True
                image = Image.open(response.raw)
                self._img_width, self._img_height = image.size
                image.save(self._image_file_path, format=image.format)
                self._logger.info('Downloaded image form source {} at {}'.format(
                    self._source_img_url, self._image_file_path))

            except requests.exceptions.MissingSchema as e:
                self._logger.exception(
                    '"source_image_url" attribute must be a URL.')
            except requests.exceptions.ConnectionError as e:
                self._logger.exception(
                    'Failed to fetch image from {}'.format(self._source_img_url))
        else:
            image = Image.open(self._image_file_path)
            self._img_width, self._img_height = image.size
            self._logger.warn('WARN: Skipping file download since it already exist @ {}\n'.format(
                self._image_file_path))

    def _resize_image(self, image_path):
        file_name = self._file_name + self._file_ext
        self._resized_image_path = os.path.join(
            self._resized_image_dir, file_name)

        image = cv2.imread(image_path)
        # old_size is in (height, width) format
        original_size = image.shape[:2]
        required_size = max(self._required_img_height,
                            self._required_img_width)

        self._ratio = float(required_size)/max(original_size)
        self._new_size = tuple([int(x*self._ratio) for x in original_size])

        # new_size should be in (width, height) format
        image = cv2.resize(image, (self._new_size[1], self._new_size[0]))

        delta_w = required_size - self._new_size[1]
        delta_h = required_size - self._new_size[0]

        self._top_border, self._bottom_border = delta_h//2, delta_h - \
            (delta_h//2)
        self._left_border, self._right_border = delta_w//2, delta_w - \
            (delta_w//2)

        if not os.path.exists(self._resized_image_path):
            color = [0, 0, 0]
            new_image = cv2.copyMakeBorder(image,
                                           self._top_border, self._bottom_border,
                                           self._left_border, self._right_border,
                                           cv2.BORDER_CONSTANT, value=color)

            cv2.imwrite(self._resized_image_path, new_image)
            self._logger.info('Resized image at {}.jpg'.format(
                self._resized_image_path))
        else:
            self._logger.warn('WARN: Skipping file resizing since it already exist @ {}\n'.format(
                self._resized_image_path))

    def _generate_annotations(self, logger, json_labels):
        """ Handle different annotation type. """
        if self._annotation_type == self.ANNOTATION_PASCAL_VOC:
            self._generate_pascal_voc_file(logger, json_labels, apply_reduction=True)
        elif self._annotation_type == self.ANNOTATION_COCO:
            self._generate_coco_file(logger,
                                     json_labels, apply_reduction=True, debug=False)
        else:
            self._logger.error(
                'Unknown annotation type : {}'.format(self._annotation_type))
            raise ValueError()

    def _generate_pascal_voc_file(self, logger, json_labels, apply_reduction=False, debug=False):
        """ Transform WKT polygon to pascal voc. """
        config = {
            'labelbox_id': self._id,
            'project_name': self._project_name,
            'json_labels': json_labels,
            'annotation_dir': self._annotations_dir,
            'apply_reduction': apply_reduction,
            'debug': debug
        }

        if apply_reduction:
            config.update({
                'image_path': self._resized_image_path,
                'image_width': self._required_img_width,
                'image_height': self._required_img_height,
                'top_border': self._top_border,
                'bottom_border': self._bottom_border,
                'left_border': self._left_border,
                'right_border': self._right_border,
                'image_ratio': self._ratio
            })
        else:
            config.update({
                'image_path': self._image_file_path,
                'image_width': self._img_width,
                'image_height': self._img_height,
                'top_border': None,
                'bottom_border': None,
                'left_border': None,
                'right_border': None,
                'image_ratio': 1
            })
        generator = PascalVOCGenerator(logger, config)

    def _generate_coco_file(self, logger, json_labels, apply_reduction=True, debug=False):
        """ Transform WKT polygon to coco format. """

        coco = {
            'info': None,
            'images': [],
            'annotations': [],
            'licenses': [],
            'categories': []
        }

        coco['info'] = {
            'year': dt.datetime.now().year,
            'version': None,
            'description': self._project_name,
            'contributor': self._created_by,
            'url': 'labelbox.io',
            'date_created': dt.datetime.now().isoformat()
        }

        image = {
            "id": self._id,
            "file_name": self._file_name,
            "license": None,
            "flickr_url": self._source_img_url,
            "coco_url": self._source_img_url,
            "date_captured": None,
        }

        if apply_reduction:
            image.update({
                "width": self._required_img_width,
                "height": self._required_img_height,
            })
        else:
            image.update({
                "width": self._img_width,
                "height": self._img_height,
            })

        coco['images'].append(image)

        for label_name, polygon in json_labels.items():
            try:
                # check if label category exists in 'categories' field
                label_id = [c['id'] for c in coco['categories']
                            if c['supercategory'] == label_name][0]
            except IndexError as e:
                label_id = len(coco['categories']) + 1
                category = {
                    'supercategory': label_name,
                    'id': len(coco['categories']) + 1,
                    'name': label_name
                }
                coco['categories'].append(category)

            multi_polygons = wkt.loads(polygon)
            for m in multi_polygons:
                segmentation = []
                for x, y in m.exterior.coords:
                    if apply_reduction:
                        segmentation.extend(
                            [x * self._ratio, self._required_img_height - y * self._ratio - self._bottom_border])
                    else:
                        segmentation.extend([x, self._img_height-y])

                annotation = {
                    "id": len(coco['annotations']) + 1,
                    "image_id": self._id,
                    "category_id": label_name,
                    "segmentation": [segmentation],
                    "iscrowd": 0,
                }

                if apply_reduction:
                    annotation.update({
                        "area": m.area * self._ratio,
                        "bbox": [m.bounds[0] * self._ratio, m.bounds[1] * self._ratio,
                                 (m.bounds[2]-m.bounds[0]) * self._ratio,
                                 (m.bounds[3]-m.bounds[1]) * self._ratio],

                    })
                else:
                    annotation.update({
                        "area": m.area,  # float
                        "bbox": [m.bounds[0], m.bounds[1],
                                 m.bounds[2]-m.bounds[0],
                                 m.bounds[3]-m.bounds[1]],
                    })

                if debug:
                    image = cv2.imread(self._resized_image_path)
                    top_xy = (int(segmentation[2]), int(segmentation[3]))
                    bottom_xy = (int(segmentation[6]), int(segmentation[7]))
                    self.show_bounding_box(image, top_xy, bottom_xy)

                coco['annotations'].append(annotation)

        file_name = '{}.json'.format(self._file_name)
        coco_path = os.path.join(self._annotations_dir, 'coco')
        if not os.path.exists(coco_path):
            os.mkdir(coco_path)
        coco_file = os.path.join(coco_path, file_name)

        if not os.path.exists(coco_file):
            with open(coco_file, 'w+') as coco_file:
                coco_file.write(json.dumps(coco))
            self._logger.info(
                'Coco annotation file has been created at {}\n'.format(str(coco_file)))
        else:
            self._logger.warning(
                'WARN: Skipping file creation since it already exist at {}\n'.format(coco_file))

    def show_bounding_box(self, image, top_xy, bottom_xy):
        cv2.rectangle(image, top_xy, bottom_xy, (0, 255, 0), 1)
        cv2.imshow('Bounding box', image)
        cv2.waitKey(1000)
        cv2.destroyAllWindows()
