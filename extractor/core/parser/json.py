import json 

from extractor.core.data.labelbox import LabeledImage

class JSONParser:
    """ Custom json parsing utility to handle labelbox.io extraction file. """

    def __init__(self, json_file, logger):
        self._logger = logger(__name__)
        self._json_file = json_file

        self._extract_json_from_file()
        self.parse_extracted_data_to_object(logger)
    
    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'{self._json_file!r}, {self._logger!r}')
    
    def __str__(self):
        return f'A json parser for file {self._json_file}'


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
            image = LabeledImage(logger, **entry)
            labeled_imgs.append(image)
        
        import IPython;IPython.embed()
        

from abc import ABCMeta, abstractmethod    
class AbstractLabelETL:
    """ 
    A utility class for label extraction transformation and load (ETL) .
    
    Provides way to extract labelbox.io data an transform it 
    to transform data to meet multiple deep-learning framework needs.
    """ 

    def __init__(self, labeled_images):
        self._labeled_images = labeled_images
    
    @abstractmethod
    def create_label_map(self):
        pass
    
    @abstractmethod
    def prepare_annotation(self):
        pass

class ETLTensorflow(AbstractLabelETL):
    LABEL_MAP_FILE_NAME = 'label_map.pbtxt'

    def __init__(self, labeled_images):
        super().__init__(labeled_images)
    

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'{self._labeled_images!r})') 

    def __str__(self):
        return (f'An label utility class to extract transform and lood' 
                f'labeled in tensorflow object detection required format')       

    def create_label_map(self):
        #TODO: Continue here
        #labels = [label.labels for item in self.labeled_images]

        labels = []
        for label in self:
            labels.extend(label.labels)

        label_names = {label.name for label in labels}     
    
        
