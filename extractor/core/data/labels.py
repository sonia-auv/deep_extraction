
class Label:
    """ Custom class matching label json object of labelbox.io. """

    def __init__(self, name, polygon):
        self.name = name
        self.wkt_polygon = polygon

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'{self.name!r}, {self.wkt_polygon!r})')
    
    def __str__(self):
        return f'A label named {self.name}'

    #TODO: Darknet pascal voc
    #TODO: Complete conversion to pascal voc 
    #TODO: Complete conversion to mscoco


    
