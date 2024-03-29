import argparse
import json
import os

from extractor.extractor import Extractor
from utils.logger import create_logger


class Main():
    """ Script: Tranform extracted json from labelbox.io  to python objects."""

    def __init__(self):
        self.main()

    def parse_args(self):
        """ Parse args passed on while calling the script. """

        args_parser = argparse.ArgumentParser()

        args_parser.add_argument('-f', '--json_file_dir',
                                 default=None,
                                 dest='json_file_dir',
                                 type=str,
                                 required=True,
                                 help='Path to json file containing label data')

        args_parser.add_argument('-o', '--output_dir',
                                 default=None,
                                 dest='output_dir',
                                 type=str,
                                 required=True,
                                 help='Path to destination directory where images and bounding box are created')

        args_parser.add_argument('-d', '--detection_dir',
                                 default=None,
                                 dest='detection_dir',
                                 type=str,
                                 required=False,
                                 help='Path to base base deep_detection directory')

        args_parser.add_argument('-iw', '--required_img_width',
                                 default=300,
                                 dest='required_img_width',
                                 type=int,
                                 required=False,
                                 help='Model required image width')

        args_parser.add_argument('-ih', '--required_img_height',
                                 default=300,
                                 dest='required_img_height',
                                 type=int,
                                 required=False,
                                 help='Model required image height')

        return args_parser.parse_args()

    def main(self):
        """ Application main method. """
        parsed_args = self.parse_args()

        extractor = Extractor(logger=create_logger,
                              json_file=parsed_args.json_file_dir,
                              output_dir=parsed_args.output_dir,
                              detection_dir=parsed_args.detection_dir,
                              required_img_width=parsed_args.required_img_width,
                              required_img_height=parsed_args.required_img_height,)


if __name__ == '__main__':
    main = Main()
