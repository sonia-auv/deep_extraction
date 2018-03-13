import json 

from extractor.core.data.labelbox import LabeledImage

class JSONParser:
    """ Custom json parsing utility to handle labelbox.io extraction file. """

    def __init__(self, logger, *args, **kwargs):
        self._logger = logger(__name__)
        self._json_file = kwargs['json_file']
        self._images_dir = kwargs['images_dir']
        self._resized_dir = kwargs['resize_dir']
        self._annotations_dir = kwargs['annotations_dir']
        self._required_img_width = kwargs['required_img_width']
        self._required_img_height = kwargs['required_img_height']
        self._annotation_type = kwargs['annotation_type']
        self._augment_images = kwargs['augment_images']

        self._extract_json_from_file()
        self.parse_extracted_data_to_object(logger)
    
    # def __repr__(self):
    #     return (f'{self.__class__.__name__}('
    #             f'{self._json_file!r}, {self._logger!r}')
    
    # def __str__(self):
    #     return f'A json parser for file {self._json_file}'


    def _extract_json_from_file(self):
        """ Read file and extract contained json data. """
        self._logger.info("Opening json file and reading contained data.")
        with open(self._json_file, 'r') as data_file:
            data = data_file.read()
            self._json_data = json.loads(data)
        self._logger.info("Extracting data from json file completed with success.")

    def parse_extracted_data_to_object(self, logger):
        self._logger.info('Parsing extracted data to generate custom object.')
        labeled_imgs = []
        for entry in self._json_data:
            entry['Images Dir'] = self._images_dir
            entry['Annotations Dir'] = self._annotations_dir
            entry['Required Image Width'] = self._required_img_width
            entry['Required Image Height'] = self._required_img_height
            entry['Annotation Type'] = self._annotation_type
            entry['Resized Image Dir'] = self._resized_dir
            entry['Augment Images'] = self._augment_images
            image = LabeledImage(logger, **entry)
            labeled_imgs.append(image)
        
