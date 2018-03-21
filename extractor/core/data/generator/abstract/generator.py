from abc import ABCMeta, abstractmethod


class AbstractGenerator:
    __metaclass__ = ABCMeta
    SKIPPED_LABEL = 'Skip'

    def __init__(self, logger, config):
        self._logger = logger(__name__)
        self._labelbox_id = config['labelbox_id']
        self._project_name = config['project_name']
        self._json_labels = config['json_labels']
        self._annotation_dir = config['annotation_dir']
        self._image_path = config['image_path']
        self._image_width = config['image_width']
        self._image_height = config['image_height']
        self._top_border = config['top_border']
        self._bottom_border = config['bottom_border']
        self._left_border = config['left_border']
        self._right_border = config['right_border']
        self._image_ratio = config['image_ratio']
        self._apply_reduction = config['apply_reduction']
        self._debug = config['debug']

        self.label_names = set()

        self._execute()

    @abstractmethod
    def _parse_label(self):
        pass

    @abstractmethod
    def _transform_to_format(self, polygon):
        pass

    @abstractmethod
    def _debug_bounding_box(self, xy_coords):
        pass

    @abstractmethod
    def _execute(self):
        pass
