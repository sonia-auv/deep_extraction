from .base import BaseAnnotationGenerator

class PascalVOCAnnotationGenerator(BaseAnnotationGenerator):

    def __init__(self, json_data, output_file_path):
        super().__init__(json_data, output_file_path)
    
     #TODO: Complete abstraction of annotation generator
    def __repr__(self):
        pass
    
    def __str__(self):
        pass