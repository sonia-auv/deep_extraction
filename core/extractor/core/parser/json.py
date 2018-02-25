import json 
from .utils.json import create_logger

class JSONParser:
    """ Custom json parsing utility to handle labelbox.io extraction file. """

    def __init__(self, json_file, logger):
        self._logger = create_logger(__name__)
        self._json_file = json_file
        
    def _extract_json_from_file(self):
        """ Read file and extract contained json data. """
        self._logger.info("Opening json file and reading contained data.")
        with open(self._json_file, 'r') as data_file:
            data = data_file.read()
            self.json_data = json.loads(data)
        self._logger.info("Extracting data from json file completed with success.")

    def parse_extracted_data_to_object(self):
        self._logger.info('Parsing extracted data to generate custom object.')



        
