from abc import ABCMeta, abstractmethod


class AbstractGenerator:
    __metaclass__ = ABCMeta
    SKIPPED_LABEL = 'Skip'

    def __init__(self, logger):
        self._logger = logger(__name__)

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
