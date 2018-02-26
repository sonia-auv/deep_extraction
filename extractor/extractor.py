import os

from .core.parser.json import JSONParser

class Extractor:
    """ Labelbox.io label object extractor. """

    def __init__(self, logger, *args, **kwargs):
        self._logger = logger(__name__)
        self._json_file = kwargs['json_file']
        self._output_path = kwargs['output_path']

        self._prepare_output_path()
        self._extract_labels_from_json(logger)


    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'{self._json_file!r}, {self._output_path!r}, )')
    
    def __str__(self):
        return f'An labebox.io object extractor with output path {self._output_path}'


    def _prepare_output_path(self):
        """ Prepare output folder to receive images and bounding box data. """
        
        self._image_dir = os.path.join(self._output_path, 'images')
        self._bounding_box_dir = os.path.join(self._output_path, 'bouding_box')
        
        if not os.path.exists(self._output_path):
            os.makedirs(self._output_path)

        if not os.path.exists(self._image_dir):
            os.makedirs(self._image_dir)

        if not os.path.exists(self._bounding_box_dir):
            os.makedirs(self._bounding_box_dir)

    def _extract_labels_from_json(self, logger):
        json_parser = JSONParser(self._json_file, logger)

    
    #TODO: Need to get access





    
