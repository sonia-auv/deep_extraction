import os

class Extractor:
    """ Labelbox.io label object extractor. """

    def __init__(self, logger, *args, **kwargs):
        self.logger = logger(__name__)
        self.json_file = kwargs['json_file']
        self.output_path = kwargs['output_path']

        self.prepare_output_path()

    def prepare_output_path(self):
        """ Prepare output folder to receive images and bounding box data. """
        
        self.image_dir = os.path.join(self.output_path, 'images')
        self.bounding_box_dir = os.path.join(self.output_path, 'bouding_box')
        
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)

        if not os.path.exists(self.bounding_box_dir):
            os.makedirsO(self.bounding_box_dir)
    
    



    
