import os
import json
import requests
import cv2
import datetime as dt
import numpy as np
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
        self._file_name = self._source_img_url.rsplit('/', 1)[-1].split('.')[0]
        self._file_ext = '.' + self._source_img_url.split("/")[-1].split('.')[1]
        self._download_image(kwargs['Label'])
        self._generate_annotations(kwargs['Label'])
       

    def _download_image(self, json_labels):
        """ Download image from provided link (Cloud link)."""
        file_path = os.path.join(self._images_dir, self._file_name)
        self._image_file_path = file_path + self._file_ext

        if not os.path.exists(self._image_file_path):
            try:
                response = requests.get(self._source_img_url, stream=True)
                response.raw.decode_content = True

                image = Image.open(response.raw)
                self._img_width, self._img_height = image.size
                image.save(self._image_file_path, format=image.format)
                
                self._image_file_path = file_path + self._file_ext
                self._logger.info('Downloaded image form source {} at {}'.format(self._source_img_url, self._image_file_path))

                self._resize_image(self._image_file_path)

            except requests.exceptions.MissingSchema as e:
                self._logger.exception('"source_image_url" attribute must be a URL.')
            except requests.exceptions.ConnectionError as e:
                self._logger.exception('Failed to fetch image from {}'.format(self._source_img_url))
        else:
            self._image_file_path = file_path + self._file_ext
            image = Image.open(self._image_file_path)
            self._img_width, self._img_height = image.size
            self._logger.warn('WARN: Skipping file download since it already exist @ {}\n'.format(self._image_file_path))

    def _resize_image(self, image_path):

        file_name = self._file_name + self._file_ext
        file_path = os.path.join(self._resized_image_dir, file_name)

        if not os.path.exists(file_path):
            image = cv2.imread(image_path)
            original_size = image.shape[:2] # old_size is in (height, width) format
            required_size = max(self._required_img_height, self._required_img_width)

            self.ratio = float(required_size)/max(original_size)    
            self.new_size = tuple([int(x*self.ratio) for x in original_size])

            # new_size should be in (width, height) format
            image = cv2.resize(image, (self.new_size[1], self.new_size[0])) 

            delta_w = required_size - self.new_size[1]
            delta_h = required_size - self.new_size[0]
            
            self.top_border, self.bottom_border = delta_h//2, delta_h-(delta_h//2)
            self.left_border, self.right_border = delta_w//2, delta_w-(delta_w//2)

            color = [0, 0, 0]

            new_image = cv2.copyMakeBorder(image, 
                                            self.top_border, self.bottom_border,
                                            self.left_border, self.right_border,
                                            cv2.BORDER_CONSTANT, value=color)

            cv2.imwrite(file_path, new_image)

         
            self._logger.info('Resized image at {}.jpg'.format(file_path))
        else:
             self._logger.warn('WARN: Skipping file resizing since it already exist @ {}\n'.format(file_path))

    def _generate_annotations(self, json_labels):
        """ Handle different annotation type. """
        if self._annotation_type == self.ANNOTATION_PASCAL_VOC:  
            self._generate_pascal_voc_file(json_labels, apply_reduction=True)  
        elif self._annotation_type == self.ANNOTATION_COCO:
            pass
            self._generate_coco_file(json_labels, apply_reduction=True)
        else:
            self._logger.error('Unknown annotation type : {}'.format(self._annotation_type))
            raise ValueError()


    def _generate_pascal_voc_file(self, json_labels, apply_reduction=False):
        """ Transform WKT polygon to pascal voc. """
        self._logger.info('Transforming shapely wtk polygon format to pascal voc.\n')
        xml_writer = PascalWriter(self._image_file_path, self._img_width, self._img_height)

        for label, polygon in json_labels.items():
            multipolygon = wkt.loads(polygon)
            for m in multipolygon:
                xy_coords = []
                for x, y in m.exterior.coords:
                    if apply_reduction:
                        new_x = int(x*self.ratio) 
                        new_y = int(y*self.ratio)
                        
                        #TODO: Handle 4 cases
                        xy_coords.extend([new_x, self._required_img_height - new_y - self.bottom_border])
                    else:
                        xy_coords.extend([x, self._img_height-y])
            
                # remove last polygon if it is identical to first point
                if xy_coords[-2:] == xy_coords[:2]:
                    xy_coords = xy_coords[:-2]
                
                file_name = self._file_name + self._file_ext
                file_path = os.path.join(self._resized_image_dir, file_name)

                image = cv2.imread(file_path)

                #print(xy_coords)
                top_xy = (xy_coords[2], xy_coords[3])
                bottom_xy = (xy_coords[6], xy_coords[7])

                self.show_bounding_box(image, top_xy, bottom_xy)
            
                xml_writer.addObject(name=label.lower(), xy_coords=xy_coords)

        file_name = '{}.xml'.format(self._file_name)
        xml_file_path = os.path.join(self._annotations_dir, file_name)

        if not os.path.exists(xml_file_path):
            xml_writer.save(xml_file_path)
            self._logger.info('Pascal VOC annotation file create for image {}.\n\n'.format(self._file_name))
        else:
            self._logger.info('WARN: Skipping file creation since it already exist at {}\n'.format(xml_file_path))

    def show_bounding_box(self, image, top_xy, bottom_xy):
        cv2.rectangle(image, top_xy, bottom_xy, (255, 0, 0), 1)
        cv2.imshow('Bounding box',image)
        cv2.waitKey(1000)
        cv2.destroyAllWindows()


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
            'year': dt.datetime.now().year,
            'version': None,
            'description': self._project_name,
            'contributor': self._created_by,
            'url': 'labelbox.io',
            'date_created': dt.datetime.now().isoformat()
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
        annotation_file = os.path.join(self._annotations_dir, '{}.json'.format(file_name))
        
    
        with open(annotation_file, 'w+') as coco_file:
            coco_file.write(json.dumps(coco))
        
        self._logger.info('Coco annotation file has been created at {}\n'.format(str(annotation_file)))
