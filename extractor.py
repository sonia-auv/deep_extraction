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

        args_parser.add_argument('-f', '--json_file_path',
                                 default=None,
                                 required=True,
                                 help='Path to json file containing label data')

        args_parser.add_argument('-o', '--output_path',
                                 default=None,
                                 required=True,
                                 help='Path to destination directory where images and bounding box are created')


        return args_parser.parse_args()


    def main(self):
        """ Application main method. """
        result = self.parse_args()

        extractor = Extractor(logger=create_logger,
                              json_file=result.json_file_path,
                              output_path=result.output_path)


if __name__ == '__main__':
    main = Main()
