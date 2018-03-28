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


class LabeledImagesMSCOCO:
    """ Custom class matching returned json object of labelbox.io. """

    def __init__(self, logger, *args, **kwargs):
        self._logger = logger(__name__)
        self._json_data = kwargs['json_data']
        self._image_dir = kwargs['image_dir']
        self._resized_image_dir = kwargs['resized_image_dir']
        self._required_img_width = kwargs['required_image_width']
        self._required_img_height = kwargs['required_image_height']


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
        self.label_names = set()
        self._file_name = self._source_img_url.rsplit('/', 1)[-1].split('.')[0]
        self._file_ext = '.' + \
            self._source_img_url.split("/")[-1].split('.')[1]
        self._download_image(kwargs['Label'])
        self._resize_image(self._image_file_path)
        self._generate_pascal_voc_file(logger, kwargs['Label'], apply_reduction=True, debug=True)

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

        img = cv2.imread(image_path)

        height, width = img.shape[:2]
        scaled_height = 300
        scaled_width = 300

        # interpolation method
        if height > scaled_height or scaled_width > scaled_width:  # shrinking image
            interp = cv2.INTER_AREA
        else:  # stretching image
            interp = cv2.INTER_CUBIC

        # aspect ratio of image
        aspect = float(width)/height

        # factors to scale bounding box values
        self._x_factor = width / scaled_width
        self._y_factor = height / scaled_height

        # compute scaling and pad sizing
        if aspect > 1:  # horizontal image
            new_width = scaled_width
            new_height = np.round(new_width/aspect).astype(int)
            pad_vert = (scaled_height-new_height)/2
            pad_top, pad_bot = np.floor(pad_vert).astype(int), np.ceil(pad_vert).astype(int)
            pad_left, pad_right = 0, 0
        elif aspect < 1:  # vertical image
            new_height = scaled_height
            new_width = np.round(new_height*aspect).astype(int)
            pad_horz = (scaled_width-new_width)/2
            pad_left, pad_right = np.floor(pad_horz).astype(int), np.ceil(pad_horz).astype(int)
            pad_top, pad_bot = 0, 0
        else:  # square image
            new_height, new_width = scaled_height, scaled_width
            pad_left, pad_right, pad_top, pad_bot = 0, 0, 0, 0

        # set pad color
        # color image but only one color provided
        if len(img.shape) is 3 and not isinstance(0, (list, tuple, np.ndarray)):
            padColor = [0]*3

        # scale and pad
        scaled_img = cv2.resize(img, (new_width, new_height), interpolation=interp)
        scaled_img = cv2.copyMakeBorder(
            scaled_img, pad_top, pad_bot, pad_left, pad_right, borderType=cv2.BORDER_CONSTANT, value=0)

        if not os.path.exists(self._resized_image_path):
            cv2.imwrite(self._resized_image_path, scaled_img)
            self._logger.info('Resized image at {}.jpg'.format(
                self._resized_image_path))
        else:
            self._logger.warn('WARN: Skipping file resizing since it already exist @ {}\n'.format(
                self._resized_image_path))

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
                'x_factor': self._x_factor,
                'y_factor': self._y_factor,
            })
        else:
            config.update({
                'image_path': self._image_file_path,
                'image_width': self._img_width,
                'image_height': self._img_height,
                'x_factor': 1,
                'y_factor': 1,
            })
        generator = PascalVOCGenerator(logger, config)
        self.label_names.update(generator.label_names)

    def show_bounding_box(self, image, top_xy, bottom_xy):
        cv2.rectangle(image, top_xy, bottom_xy, (0, 255, 0), 1)
        cv2.imshow('Bounding box', image)
        cv2.waitKey(1000)
        cv2.destroyAllWindows()
