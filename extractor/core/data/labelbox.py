import os
import requests
from PIL import Image
from shapely import wkt
from pascal_voc_writer import Writer as PascalWriter

class LabeledImage:
    """ Custom class matching returned json object of labelbox.io. """

    ANNOTATION_PASCAL_VOC = 'Pascal VOC'
    ANNOTATION_COCO = 'COCO'

    def __init__(self, logger, *args, **kwargs):
        self._logger = logger(__name__)
        self._id = kwargs['ID']
        self._source_img_url = kwargs['Labeled Data']
        self._created_by = kwargs['Created By']
        self._project_name = kwargs['Project Name']
        self._seconds_to_label = kwargs['Seconds to Label']
        self._images_dir = kwargs['Images Dir']
        self._annotations_dir = kwargs['Annotations Dir']
        self._required_img_height = kwargs['Required Image Height']
        self._required_img_width = kwargs['Required Image Width']
        self._annotation_type = kwargs['Annotation Type']
        self._file_name = self._source_img_url.rsplit('/', 1)[-1]
        self._download_image()
        self._generate_annotations()
    
    

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'{self._logger!r}, '
                f'{self._id!r}, {self._source_img_url!r}, '
                f'{self._created_by!r}, '
                f'{self._project_name!r}, {self._seconds_to_label})')
    
    def __str__(self):
        return f'A LabeledImage object from image {self._source_img_url} with id : {self._id}'
    def _download_image(self):
        """ Download image from provided link (Cloud link)."""
        try:
            response = requests.get(self._source_img_url, stream=True)
        except requests.exceptions.MissingSchema as e:
            self._logger.exception('"source_image_url" attribute must be a URL.')
        except requests.exceptions.ConnectionError as e:
            self._logger.exception(f'Failed to fetch image from {self._source_img_url}.')
        
        response.raw.decode_content = True
        
        im = Image.open(response.raw)
        image_name = f'{self._file_name}.jpg'
        self._image_file_path = os.path.join(self._images_dir, image_name)
        im.save(self._image_file_path, format=im.format)
        self._img_width , self._img_height = im.size
        self._logger.info(f'Downloaded image form source {self._source_img_url} at {self._image_file_path}')

    def _generate_annotations(self):
        """ Handle different annotation type. """
        if self._annotation_type == ANNOTATION_PASCAL_VOC:  
            self._generate_pascal_voc_file(kwargs['Label'])  
        elif self._annotation_type == ANNOTATION_COCO:
            self._generate_coco_file()
        else:
            self._logger.error(f'Unknown annotation type : {self._annotation_type}')
            raise ValueError()


    def _generate_pascal_voc_file(self, json_labels, apply_reduction=False):
        """ Transform WKT polygon to pascal voc. """
        self._logger.info(f'Transforming shapely wtk polygon format to pascal voc.')
        xml_writer = PascalWriter(self._image_file_path, self._img_width, self._img_height)

        for label, polygon in json_labels.items():
            multipolygon = wkt.loads(polygon)
            for m in multipolygon:
                xy_coords = []
                for x, y in m.exterior.coords:
                    
                    if apply_reduction:
                        #TODO:Complete data conversion according to model input size
                        #x_factor = x / self._required_img_width
                        #y_factor = y / self._required_img_height

                        #new_x = x / x_factor
                        #new_y = y / y_factor
                        #xy_coords.extend([new_x, self._img_height-new_y])
                    else:
                        xy_coords.extend([x, self._img_height-y])
            
                # remove last polygon if it is identical to first point
                if xy_coords[-2:] == xy_coords[:2]:
                    xy_coords = xy_coords[:-2]
                
                xml_writer.addObject(name=label.lower(), xy_coords=xy_coords)

        xml_writer.save(os.path.join(self._annotations_dir, f'{self._file_name}.xml'))
        self._logger.info(f'Pascal VOC annotation file create for image {self._file_name}.')


    def _generate_coco_file(self, json_labels):
        """ Transform WKT polygon to coco format. """
        raise NotImplementedError('To be implemented')


