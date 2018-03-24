import json
import os

from shapely import wkt
from extractor.core.data.labelbox import LabeledImagePascalVOC  # , LabeledImagesCOCO


class JSONParser:
    """ Custom json parsing utility to handle labelbox.io extraction file. """

    def __init__(self, logger, *args, **kwargs):
        self._logger = logger(__name__)
        self._json_file = kwargs['json_file']
        self._images_dir = kwargs['images_dir']
        self._resized_dir = kwargs['resize_dir']
        self._output_dir = kwargs['output_dir']
        self._annotations_dir = kwargs['annotations_dir']
        self._required_img_width = kwargs['required_img_width']
        self._required_img_height = kwargs['required_img_height']
        self._annotation_type = kwargs['annotation_type']

        self._extract_json_from_file()
        self.parse_extracted_data_to_object(logger)

    def __str__(self):
        return 'A json parser for file {}'.format(self._json_file)

    def _extract_json_from_file(self):
        """ Read file and extract contained json data. """
        self._logger.info("Opening json file and reading contained data.")
        with open(self._json_file, 'r') as data_file:
            data = data_file.read()
            self._json_data = json.loads(data)

            json_temp = []
            for labels in self._json_data:
                try:
                    for label in labels.items():
                        polygon = wkt.loads(label)
                except:
                    print('FUCKKKKKKKKKKKKKKKKKKKKKKKKKkkkk')

        self._logger.info(
            "Extracting data from json file completed with success.")

    def parse_extracted_data_to_object(self, logger):
        self._logger.info('Parsing extracted data to generate custom object.')
        labeled_imgs = []

        if self._annotation_type == 'Pascal VOC':
            for entry in self._json_data:
                entry['Images Dir'] = self._images_dir
                entry['Annotations Dir'] = self._annotations_dir
                entry['Required Image Width'] = self._required_img_width
                entry['Required Image Height'] = self._required_img_height
                entry['Annotation Type'] = self._annotation_type
                entry['Resized Image Dir'] = self._resized_dir

                image = LabeledImagePascalVOC(logger, **entry)
                labeled_imgs.append(image)

            self._generate_label_map(labeled_imgs)
            self._generate_file_map(labeled_imgs)

        elif self._annotation_type == 'COCO':
            # TODO: Complete label map generation
            raise NotImplementedError('COCO annotation extraction not yet completed')
            # config = {
            #     'json_data': self._json_data,
            #     'image_dir': self._images_dir,
            #     'resized_image_dir': self._resized_dir,
            #     'annotations_dir': self._annotations_dir,
            #     'required_image_width': self._required_img_width,
            #     'required_image_height': self._required_img_height
            # }
            # images = LabeledImagesMSCOCO(logger, **config)

    def _generate_file_map(self, labeled_images):
        file_path = os.path.join(self._output_dir, 'trainval.txt')

        file_names = []
        for label in labeled_images:
            file_names.append(label._file_name)

        with open(file_path, 'w') as file_:
            for file_name in file_names:
                file_.write("{}\n".format(file_name))

    def _generate_label_map(self, labeled_images):

        label_names = set()
        for label in labeled_images:
            label_names.update(label.label_names)

        label_names = tuple(label_names)

        data = []
        first_line = 'item {\n'
        second_line = '  id: {}\n'
        third_line = '  name: \'{}\'\n'
        fourth_line = '}'

        for index, label_name in enumerate(label_names):
            first_line = 'item {\n'
            second_line = '  id: {}\n'.format(index + 1)
            third_line = '  name: \'{}\'\n'.format(label_name)
            fourth_line = '}\n'

            temp = first_line + second_line + third_line + fourth_line
            data.append(temp)

        file_path = os.path.join(self._output_dir, 'label_map.pbtxt')

        with open(file_path, 'w') as label_file:
            label_file.writelines(data)
