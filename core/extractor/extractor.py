class Extractor:
    """ Labelbox.io label object extractor. """

    def __init__(self, *args, **kwargs):
        self.json_file = kwargs['json_file']
        self.output_path = kwargs['output_path']

        
    
