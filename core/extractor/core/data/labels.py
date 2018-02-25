from shapely.wkt import loads as wkt_loads

class LabelboxData:
    """ Custom class matching returned json object of labelbox.io. """

    def __init__(self, *args, **kwargs):
        self.id = kwargs['ID']
        self.source_img_url = kwargs['Labeled Data']
        self.labels = self.parse_labels(kwargs['Label'])
        self.created_by = kwargs['Created By']
        self.project_name = kwargs['Project Name']
        self.seconds_to_label = kwargs['Seconds to Label']

    def parse_labels(self, json_labels):
        """ Parse json labels and generate custom label object. """
        labels = []
        for name , polygon in json_labels.iteritems():
            label = Label(name, polygon)
            labels.append(label)
        
        return labels

class Label:
    """ Custom class matching label json object of labelbox.io. """

    def __init__(self, name, polygon):
        self.name = name
        self.wkt_polygon = wkt_loads(polygon)

    
