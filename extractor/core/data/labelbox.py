from shapely.wkt import loads as wkt_loads

from .labels import Label

class LabeledImage:
    """ Custom class matching returned json object of labelbox.io. """

    def __init__(self, logger, *args, **kwargs):
        self.logger = logger(__name__)
        self.id = kwargs['ID']
        self.source_img_url = kwargs['Labeled Data']
        self.created_by = kwargs['Created By']
        self.project_name = kwargs['Project Name']
        self.seconds_to_label = kwargs['Seconds to Label']
        self.labels = self.parse_labels(kwargs['Label'])    

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'{self.logger!r}, '
                f'{self.id!r}, {self.source_img_url!r}, '
                f'{self.labels!r}, {self.created_by!r}, '
                f'{self.project_name!r}, {self.seconds_to_label})')
    
    def __str__(self):
        return f'A LabeledImage object from image {self.source_img_url} with id : {self.id}'

    def parse_labels(self, json_labels):
        """ Parse json labels and generate custom label object. """
        labels = []
        errored_labels = []

        for name , polygon in json_labels.items():
            
            ## To handle error made in labelbox.io (bug while labeling)
            try:
                wtk_polygon =  wkt_loads(polygon)
                label = Label(name, wtk_polygon)
                labels.append(label)
            except :
               msg = f'ID:{self.id}, {self.created_by}'
               print(msg)
               errored_labels.append(msg)
               self.logger.warn('Skipping label : Polygon point count < 4 ')


        return labels, errored_labels