import os

from .core.parser.json_parser import JSONParser


class Extractor:
    """ Labelbox.io label object extractor. """

    def __init__(self, logger, *args, **kwargs):
        self._logger = logger(__name__)
        self._json_file = kwargs['json_file']
        self._output_path = kwargs['output_path']
        self._required_img_width = kwargs['required_img_width']
        self._required_img_height = kwargs['required_img_height']
        self._annotation_type = kwargs['annotation_type']

        self._prepare_output_path()
        self._extract_labels_from_json(logger)

    # def __repr__(self):
    #     return (f'{self.__class__.__name__}('
    #             f'{self._json_file!r}, {self._output_path!r}, '
    #             f'{self._output_path!r}, {self._required_img_width!r}, '
    #             f'{self._required_img_height!r}, {self._annotation_type!r}, '
    #             f'{self._augment_images!r}, {self._randomize_entries!r})')

    def __str__(self):
        return 'An labebox.io object extractor with output path {}'.format(self._output_path)

    def _prepare_output_path(self):
        """ Prepare output folder to receive images and bounding box data. """

        self._image_dir = os.path.join(self._output_path, 'images')
        self._annotation_dir = os.path.join(self._output_path, 'annotations')
        self._resized_dir = os.path.join(self._output_path, 'resized')

        if not os.path.exists(self._output_path):
            os.makedirs(self._output_path)

        if not os.path.exists(self._image_dir):
            os.makedirs(self._image_dir)

        if not os.path.exists(self._annotation_dir):
            os.makedirs(self._annotation_dir)

        if not os.path.exists(self._resized_dir):
            os.makedirs(self._resized_dir)

    def _extract_labels_from_json(self, logger):

        config = {
            'json_file': self._json_file,
            'images_dir': self._image_dir,
            'output_dir': self._output_path,
            'resize_dir': self._resized_dir,
            'annotations_dir': self._annotation_dir,
            'required_img_width': self._required_img_width,
            'required_img_height': self._required_img_height,
            'annotation_type': self._annotation_type,
        }

        json_parser = JSONParser(logger, **config)
