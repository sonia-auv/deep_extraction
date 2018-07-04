import os
import shutil
from glob import glob

from .core.parser.json_parser import JSONParser


class Extractor:
    """ Labelbox.io label object extractor. """

    def __init__(self, logger, *args, **kwargs):
        self._logger = logger(__name__)
        self._json_file = kwargs['json_file']
        self._output_dir = kwargs['output_dir']
        self._detection_dir = kwargs['detection_dir']
        self._required_img_width = kwargs['required_img_width']
        self._required_img_height = kwargs['required_img_height']

        self._prepare_output_path()
        self._extract_labels_from_json(logger)
        self._copy_annotation_to_deep_detection()
        self._copy_resized_images_to_deep_detection()

    def __str__(self):
        return 'An labebox.io object extractor with output path {}'.format(self._output_dir)

    @property
    def _detection_annotation_dir(self):
        return os.path.join(self._detection_dir, 'dataset', 'annotations')

    @property
    def _detection_image_dir(self):
        return os.path.join(self._detection_dir, 'dataset', 'images')

    @property
    def _label_map_src(self):
        return os.path.join(self._output_dir, 'label_map.pbtxt')

    @property
    def _label_map_dest(self):
        return os.path.join(self._detection_annotation_dir, 'label_map.pbtxt')

    @property
    def _train_val_src(self):
        return os.path.join(self._output_dir, 'trainval.txt')

    @property
    def _train_val_dest(self):
        return os.path.join(self._detection_annotation_dir, 'trainval.txt')

    @property
    def _annotation_dir_dest(self):
        return os.path.join(self._detection_annotation_dir, 'pascal_voc')


    def _prepare_output_path(self):
        """ Prepare output folder to receive images and bounding box data. """

        self._image_dir = os.path.join(self._output_dir, 'images')
        self._annotation_dir = os.path.join(self._output_dir, 'annotations')
        self._resized_dir = os.path.join(self._output_dir, 'resized')

        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir)

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
            'output_dir': self._output_dir,
            'resize_dir': self._resized_dir,
            'annotations_dir': self._annotation_dir,
            'required_img_width': self._required_img_width,
            'required_img_height': self._required_img_height,
        }

        json_parser = JSONParser(logger, **config)


    def _copy_annotation_to_deep_detection(self):
        """ Copy annotation xml and trainval files and labelmap.pbtxt to deep_detection."""

        annotations_files = glob(os.path.join(self._annotation_dir, 'pascal_voc', '*.xml'))
        
        if os.path.exists(self._detection_dir):
            if os.path.exists(os.path.join(self._detection_annotation_dir)):
                shutil.copyfile(self._label_map_src, self._label_map_dest)
                shutil.copyfile(self._train_val_src, self._train_val_dest)

                if os.path.exists(self._annotation_dir_dest):
                    filelist = glob(os.path.join(self._annotation_dir_dest, '*.xml'))
                    for f in filelist:
                        os.remove(f)

                    for annotation_file in annotations_files:
                        file_name = os.path.basename(annotation_file)
                        new_annotation_file = os.path.join(self._annotation_dir_dest, file_name)
                        shutil.copyfile(annotation_file, new_annotation_file)

                        self._logger.info('Copied annotation file {} to {}'.format(
                            annotation_file, new_annotation_file))

    def _copy_resized_images_to_deep_detection(self):
        """ Copy resized images to deep_detection. """
        resized_image_files = glob(os.path.join(self._resized_dir, '*.jpg'))

        resized_image_files_dest = os.path.join(self._detection_dir, 'images')

        if os.path.exists(self._detection_image_dir):
            filelist = glob(os.path.join(self._detection_image_dir, '*.jpg'))
            for f in filelist:
                os.remove(f)

            for reized_image in resized_image_files:
                file_name = os.path.basename(reized_image)
                new_resized_image = os.path.join(self._detection_image_dir, file_name)
                self._logger.info('Copying image file {} to {}'.format(
                    reized_image, new_resized_image))
                shutil.copyfile(reized_image, new_resized_image)
