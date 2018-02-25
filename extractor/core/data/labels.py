
class Label:
    """ Custom class matching label json object of labelbox.io. """

    def __init__(self, name, polygon):
        self.name = name
        self.wkt_polygon = polygon

    
