from abc import ABCMeta, abstractmethod

class BaseAnnotationGenerator(metaclass=ABCMeta):

    def __init__(self, json_data, output_file_path):
        self.json_data = json_data
        self.output_path = output_file_path

    #TODO: Complete abstraction of annotation generator
    def __repr__(self):
        pass
    
    def __str__(self):
        pass