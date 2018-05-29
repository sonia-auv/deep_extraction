import argparse
import glob
import csv
import os

from glob import glob
from datetime import datetime


class GoogleCloudStorageLinkGenerator:
    """ A basic utility class to generate links to google cloud storage imported files """

    BASE_NAME = 'https://storage.googleapis.com/robosub-2018/dataset/'

    def __init__(self, image_dir, output_dir, output_name):
        self.image_dir = image_dir
        self.output_dir = output_dir
        self.output_name = output_name
        self.execute()

    def check_or_create_output_dir(self):
        """ Check if output dir exist or not and if not create it. """
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def list_subdir_file_content_and_create_csv(self):
        """ Make a list of all subdirs files and generate a list of link to google cloud storage. """
        sub_dirs = glob(self.image_dir + '*/')

        for sub_dir in sub_dirs:
            urls = []
            sub_dir_content = glob(sub_dir + '*')
            for image_path in sub_dir_content:
                splited = image_path.rsplit('/', 2)

                url = os.path.join(self.BASE_NAME, splited[1], splited[2])
                urls.append(url)

            base_name = os.path.basename(os.path.normpath(sub_dir))
            self.create_csv(urls, base_name)

    def create_csv(self, urls, sub_dir):
        """ Generate a csv file. """
        file_name = 'link_to_gcc_{}_{}.csv'.format(sub_dir, datetime.now())
        output_file = os.path.join(self.output_dir,  file_name)
        with open(output_file, 'w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_ALL)
            for url in urls:
                csv_writer.writerow([url])

    def execute(self):
        """ Main method. """
        self.check_or_create_output_dir()
        self.list_subdir_file_content_and_create_csv()


def parse_args():
    parser = argparse.ArgumentParser(description='Google cloud storage link csv generator.')

    parser.add_argument('-i', '--image_dir',
                        dest='image_dir',
                        required=True,
                        type=str,
                        help='Directory containing image for which we want to generate link')
    parser.add_argument('-o', '--output_dir',
                        dest='output_dir',
                        required=True,
                        type=str,
                        help='Directory where to create the csv file')
    parser.add_argument('-n', '--output_name',
                        dest='output_name',
                        required=True,
                        type=str,
                        help='CSV output file name')

    return parser.parse_args()


if __name__ == '__main__':

    parsed_args = parse_args()

    link_generator = GoogleCloudStorageLinkGenerator(parsed_args.image_dir,
                                                     parsed_args.output_dir,
                                                     parsed_args.output_name)
