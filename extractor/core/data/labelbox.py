import datetime as dt
import os
import json
import requests
#import cv2
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
        self._resized_image_dir = kwargs['Resized Image Dir']
        self._annotations_dir = kwargs['Annotations Dir']
        self._required_img_height = kwargs['Required Image Height']
        self._required_img_width = kwargs['Required Image Width']
        self._annotation_type = kwargs['Annotation Type']
        self._file_name = self._source_img_url.rsplit('/', 1)[-1]
        self._download_image(kwargs['Label'])
        self._generate_annotations(kwargs['Label'])
       
       
    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'{self._logger!r}, '
                f'{self._id!r}, {self._source_img_url!r}, '
                f'{self._created_by!r}, '
                f'{self._project_name!r}, {self._seconds_to_label})')
    
    def __str__(self):
        return f'A LabeledImage object from image {self._source_img_url} with id : {self._id}'

    def _download_image(self, json_labels):
        """ Download image from provided link (Cloud link)."""
        file_path = os.path.join(self._images_dir, self._file_name)

        if not os.path.exists(file_path):
            try:
                response = requests.get(self._source_img_url, stream=True)
                response.raw.decode_content = True
                im = Image.open(response.raw)
                self._resize_image(im)
                file_path = os.path.join(self._images_dir, self._file_name)
                self._image_file_path = os.path.join(file_path, im.format)
                im.save(file_path, format=im.format)
                self._img_width , self._img_height = im.size
                self._logger.info(f'Downloaded image form source {self._source_img_url} at {file_path}')
            except requests.exceptions.MissingSchema as e:
                self._logger.exception('"source_image_url" attribute must be a URL.')
            except requests.exceptions.ConnectionError as e:
                self._logger.exception(f'Failed to fetch image from {self._source_img_url}.')
        else:
            im = Image.open(file_path)
            self._img_width, self._img_height = im.size
            self._logger.warn(f'WARN: Skipping file download since it already exist @ {file_path}\n')
    
    def _resize_image(self, image):
        """ Resize downloaded image to fit neural network requirements. """
        file_path = os.path.join(self._resized_image_dir, self._file_name)
        if not os.path.exists(file_path): 
            img = cv2.resize(image, (self._required_img_width, self._required_img_height))
            img.save(file_path, format=image.format)
            
            self._logger.info(f'Resized image at {file_path}.jpg')
        else:
             self._logger.warn(f'WARN: Skipping file resizing since it already exist @ {file_path}\n')



        
    def _generate_annotations(self, json_labels):
        """ Handle different annotation type. """
        if self._annotation_type == self.ANNOTATION_PASCAL_VOC:  
            self._generate_pascal_voc_file(json_labels, apply_reduction=True)  
        elif self._annotation_type == self.ANNOTATION_COCO:
            pass
            self._generate_coco_file(json_labels, apply_reduction=True)
        else:
            self._logger.error(f'Unknown annotation type : {self._annotation_type}')
            raise ValueError()


    def _generate_pascal_voc_file(self, json_labels, apply_reduction=False):
        """ Transform WKT polygon to pascal voc. """
        self._logger.info(f'Transforming shapely wtk polygon format to pascal voc.\n')
        xml_writer = PascalWriter(self._image_file_path, self._img_width, self._img_height)

        for label, polygon in json_labels.items():
            multipolygon = wkt.loads(polygon)
            for m in multipolygon:
                xy_coords = []
                for x, y in m.exterior.coords:
                    if apply_reduction:
                        x_factor = self._img_width / self._required_img_width
                        y_factor = self._img_height / self._required_img_height

                        new_x = x / x_factor
                        new_y = y / y_factor
                        resized_height = self._img_height / y_factor
                        
                        xy_coords.extend([new_x, resized_height-new_y])
                    else:
                        xy_coords.extend([x, self._img_height-y])
            
                # remove last polygon if it is identical to first point
                if xy_coords[-2:] == xy_coords[:2]:
                    xy_coords = xy_coords[:-2]
                
                xml_writer.addObject(name=label.lower(), xy_coords=xy_coords)
        
        xml_file_path = os.path.join(self._annotations_dir, f'{self._file_name}.xml')

        if not os.path.exists(xml_file_path):
            xml_writer.save(xml_file_path)
            self._logger.info(f'Pascal VOC annotation file create for image {self._file_name}.\n\n')
        else:
            self._logger.info(f'WARN: Skipping file creation since it already exist at {xml_file_path}\n')

    def _generate_coco_file(self, json_labels, apply_reduction=True):
        """ Transform WKT polygon to coco format. """
        coco = {
            'info': None,
            'images': [],
            'annotations': [],
            'licenses': [],
            'categories': []
        }

        coco['info'] = {
            'year': dt.datetime.now(dt.timezone.utc).year,
            'version': None,
            'description': self._project_name,
            'contributor': self._created_by,
            'url': 'labelbox.io',
            'date_created': dt.datetime.now(dt.timezone.utc).isoformat()
        }

        image = {
            "id": self._id,
            "width": self._img_width,
            "height": self._img_height,
            "file_name": self._file_name,
            "license": None,
            "flickr_url": self._source_img_url,
            "coco_url": self._source_img_url,
            "date_captured": None,
        }

        coco['images'].append(image)

        for label_name, polygon in json_labels.items():
            try:
                # check if label category exists in 'categories' field
                label_id = [c['id'] for c in coco['categories']
                          if c['supercategory'] == label_name][0]
            except IndexError as e:
                label_id = len(coco['categories']) + 1
                category = {
                    'supercategory': label_name,
                    'id': len(coco['categories']) + 1,
                    'name': label_name
                }
                coco['categories'].append(category)
            
            multipolygon = wkt.loads(polygon)
            for m in multipolygon:
                segmentation = []
                for x, y in m.exterior.coords:
                    if apply_reduction:
                        x_factor = self._img_width / self._required_img_width
                        y_factor = self._img_height / self._required_img_height

                        new_x = x / x_factor
                        new_y = y / y_factor
                        resized_height = self._img_height / y_factor

                        segmentation.extend([new_x, resized_height-new_y])
                    else:
                        segmentation.extend([x, self._img_height-y])
                
                annotation = {
                    "id": len(coco['annotations']) + 1,
                    "image_id": self._id,
                    "category_id": label_id,
                    "segmentation": [segmentation],
                    "area": m.area,  # float
                    "bbox": [m.bounds[0], m.bounds[1],
                             m.bounds[2]-m.bounds[0],
                             m.bounds[3]-m.bounds[1]],
                    "iscrowd": 0
                }

                coco['annotations'].append(annotation)

        file_name = self._file_name.rsplit('.', 1)[0]
        annotation_file = os.path.join(self._annotations_dir, f'{file_name}.json')
        
    
        with open(annotation_file, 'w+') as coco_file:
            coco_file.write(json.dumps(coco))
        
        self._logger.info(f'Coco annotation file has been created at {str(annotation_file)}\n')



