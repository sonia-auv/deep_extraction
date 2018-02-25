from shapely.wkt import loads as wkt_loads

from .labels import Label

class LabeledImage:
    """ Custom class matching returned json object of labelbox.io. """

    def __init__(self, logger, *args, **kwargs):
        self.logger = logger(__name__)
        self.id = kwargs['ID']
        self.source_img_url = kwargs['Labeled Data']
        self.labels = self.parse_labels(kwargs['Label'])
        self.created_by = kwargs['Created By']
        self.project_name = kwargs['Project Name']
        self.seconds_to_label = kwargs['Seconds to Label']

    def parse_labels(self, json_labels):
        """ Parse json labels and generate custom label object. """
        labels = []

        for name , polygon in json_labels.items():
            
            ## To handle error made in labelbox.io (bug while labeling)
            try:
                wtk_polygon =  wkt_loads(polygon)
                label = Label(name, wtk_polygon)
                labels.append(label)
            except :
               self.logger.warn('Skipping label : Polygon point count < 4 ')

        return labels