import argparse
import json
import os
import random

from glob import glob


def parse_args():
    """
    Parse args passed on while calling the script.
    """
    args_parser = argparse.ArgumentParser()

    args_parser.add_argument('-j', '--json_files_folder',
                             default=None,
                             dest='json_files_folder',
                             type=str,
                             required=True,
                             help='Path to folder containing multiple json extract files from labelbox.io')

    args_parser.add_argument('-o', '--output_json_file',
                             default=None,
                             dest='output_json_file',
                             type=str,
                             required=True,
                             help='Path to json file containing all labeling data from labelbox.io')

    args_parser.add_argument('-s', '--sample_per_file',
                             dest='sample_per_file',
                             default=0,
                             type=int,
                             required=False,
                             help='Number of images to be randomly kept from a given file in the list')

    return args_parser.parse_args()


def list_json_files(folder_path):
    """
    Create a list of all .json file in a given file path

    Arguments:
        folder_path {str} - - [folder containing all json files to be extracted]

    Returns:
        [list str] - - [list containing all file path to json files]
    """
    query = os.path.join(folder_path, '*.json')
    file_list = glob(query)

    return file_list


def extract_json_from_files(json_files, sample_count):
    """
    Extract labelbox bounding box data from labelbox.io extract files.

    Arguments:
        json_files {[list(str)]} - - [list of string containg all json files path]

    Returns:
        [list(str)] - - [list containing all extracted json data]
    """
    json_data = []
    for file_ in json_files:
        with open(file_, 'r') as json_file:
            data = json.load(json_file)
            random_data = random.sample(data, sample_count)

            json_data.extend(random_data)
            print('json_data length {}'.format(len(json_data)))

    return json_data


def export_to_json_file(output_file, json_data):
    """
    Export collected data from labelbox.io extraction files to a new json file.

    Arguments:
        output_file {str]} -- [output json file path]
        json_data {[list(str)]} -- [json data to be extracted to file]
    """
    with open(output_file, 'w+') as json_file:
        json.dump(json_data, json_file)


def main():
    parsed_args = parse_args()
    json_files = list_json_files(parsed_args.json_files_folder)
    json_data = extract_json_from_files(json_files, parsed_args.sample_per_file)
    export_to_json_file(parsed_args.output_json_file, json_data)


if __name__ == '__main__':
    main()
