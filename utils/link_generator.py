import glob
import csv
import os

from datetime import datetime

class GoogleCloudStorageLinkGenerator:
    """ A basic utility class to generate links to google cloud storage imported files """
    
    BASE_NAME = 'https://storage.googleapis.com/robosub-2018'

    def __init__(self, image_dir, output_dir, output_name):
        self.image_dir = image_dir
        self.base_dir = os.path.join(self.image_dir, '*')
        self.urls = glob.glob(self.base_dir)
        self.output_file = os.path.join(output_dir, f'link_to_gcc_{output_name}_{datetime.now()}.csv')
        self.create_csv()

    def create_csv(self):
        with open(self.output_file, 'w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_ALL)
            for url in self.urls:
                url = url.replace(self.image_dir, self.BASE_NAME)
                csv_writer.writerow([url])


